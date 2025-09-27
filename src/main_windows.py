#from voice import Voice
import cv2
from ultralytics import YOLO
from utils import *
#import smbus
from time import sleep
from turn_signal_detector import TurnSignalDetector
import math
import threading
from rapidfuzz import fuzz #pip install rapidfuzz
import easyocr #pip install easyocr
import re
#import serial
#import adafruit_gps
import time
from collections import deque
import queue
import numpy as np
#import torch
#import pynmea2 #pip install pyserial pynmea2
import random
from datetime import datetime


# # =============================== 
# # IMU(MPU6050) Setup
# # ===============================
# # MPU6050 Registers
# PWR_MGMT_1   = 0x6B
# SMPLRT_DIV   = 0x19
# CONFIG       = 0x1A
# GYRO_CONFIG  = 0x1B
# INT_ENABLE   = 0x38
# ACCEL_XOUT_H = 0x3B
# ACCEL_YOUT_H = 0x3D
# ACCEL_ZOUT_H = 0x3F
# GYRO_XOUT_H  = 0x43
# GYRO_YOUT_H  = 0x45
# GYRO_ZOUT_H  = 0x47

# # For Raspberry Pi
# bus = smbus.SMBus(1)     

# # MPU6050 device address
# Device_Address = 0x68

# # Offsets provided for calibration
# Ax_offset = 0.05
# Ay_offset = -0.01
# Az_offset = -1.11
# Gx_offset = 0.29
# Gy_offset = 0.07
# Gz_offset = 0.09

# # Filtering and Thresholds
# GYRO_WINDOW = 10
# GYRO_THRESHOLD = 5.0 # degrees/sec

# # Deques for storing gyro data
# gyro_buffer = deque(maxlen=GYRO_WINDOW)

# def MPU_Init():
#     bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
#     bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
#     bus.write_byte_data(Device_Address, CONFIG, 0)
#     bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
#     bus.write_byte_data(Device_Address, INT_ENABLE, 1)

# def read_raw_data(addr):
#     high = bus.read_byte_data(Device_Address, addr)
#     low = bus.read_byte_data(Device_Address, addr + 1)
#     value = (high << 8) | low
#     if value > 32768:
#         value = value - 65536
#     return value

# def get_motion_data():
#     acc_x = read_raw_data(ACCEL_XOUT_H)
#     acc_y = read_raw_data(ACCEL_YOUT_H)
#     acc_z = read_raw_data(ACCEL_ZOUT_H)
#     gyro_x = read_raw_data(GYRO_XOUT_H)
#     gyro_y = read_raw_data(GYRO_YOUT_H)
#     gyro_z = read_raw_data(GYRO_ZOUT_H)
    
#     Ax = acc_x / 16384.0
#     Ay = acc_y / 16384.0
#     Az = acc_z / 16384.0
#     Gx = gyro_x / 131.0
#     Gy = gyro_y / 131.0
#     Gz = gyro_z / 131.0
    
#     return Ax, Ay, Az, Gx, Gy, Gz
    
# def detect_turn():
#     _, _, _, Gx, Gy, Gz = get_motion_data()
#     gyro_buffer.append(Gy)

#     # Compute moving average
#     gyro_avg = sum(gyro_buffer) / len(gyro_buffer)

#     # Determine the turn:
#     if abs(gyro_avg) > GYRO_THRESHOLD:
#         if gyro_avg > 0:
#             return "Right Turn"
#         else:
#             return "Left Turn"
#     else:
#         return "Straight"
    

# # def get_direction_and_acceleration():
# #     Ax, Ay, Az, Gx, Gy, Gz = get_motion_data()
# #     accel_magnitude = math.sqrt(Ax**2 + Ay**2 + Az**2)
    
# #     # Simple directional estimation using Ax and Ay
# #     if Ax > 0.5:
# #         direction = "Right"
# #     elif Ax < -0.5:
# #         direction = "Left"
# #     elif Ay > 0.5:
# #         direction = "Forward"
# #     elif Ay < -0.5:
# #         direction = "Backward"
# #     else:
# #         direction = "Stationary"
    
# #     return direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz


# # ========================================
# # GPS Setup
# # ========================================
# uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=30)
# gps = adafruit_gps.GPS(uart, debug=False)
# gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# gps.send_command(b'PMTK220,1000')
# last_print = time.monotonic()


# ========================================
# Turn Signal Detector Setup
# ========================================
def turn_signal_callback(prob: float, timestamp: float):
    global blinker_on
    if prob > 0.4:
        blinker_on = True
    print(f"===========================Turn Signal Probability: {prob:.4f} at {timestamp:.2f}")

def turn_signal_deactivate_callback(timestamp: float):
    global blinker_on
    blinker_on = False
    print(f"===========================Turn Signal Deactivated at {timestamp:.2f}")

turn_signal_detector = TurnSignalDetector()

# # ========================================
# # Voice Engine Setup
# # ========================================
# voice_queue = queue.Queue()

# def speak_queued(text):
#     voice_queue.put(text)

# voice = Voice("models/voice/piper.onnx")

# def voice_worker():
#     while True:
#         text = voice_queue.get() # Block until an item is available
#         voice.speak(text)
#         voice_queue.task_done()



# ========================================
# Main function integrating vision and IMU
# ========================================
def main():
    start_time = datetime.now()

    infer_imgsz = 416
    bulb_infer_imgsz = 256
    PROCESS_EVERY_N = 8
    OCR_COOLDOWN_FRAMES = 30

    print("===========================Starting turn signal detector...")
    turn_signal_detector.start_mic(
        on_detect=turn_signal_callback,
        on_deactivate=turn_signal_deactivate_callback
    )

    print("===========================Starting voice engine...")  
    # threading.Thread(target=voice_worker, daemon=True).start()

    
    l_conf_threshold=0.5 #Traffic light confidence threshold value
    b_conf_threshold=0.5 #Traffic light bulb confidence threshold value
    s_conf_threshold=0.4 #Traffic sign confidence threshold value

    diff_conf = 0.1  #To be used to find dominant color of traffic bulb
    big_font_scale = 0.6  #To be used when plot 
    small_font_scale = 0.4  #To be used when plot 
    thickness = 2 #To be used when plot 
    count = 0

    # Load YOLO model
    l_model = YOLO('models/image/best_light.pt')
    b_model = YOLO('models/image/best_bulb.pt')
    s_model = YOLO('models/image/best_sign.pt') 

    # Start video stream
    print("===========================Starting video capture...")
    #cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture('tests/video/traffic_lights/IMG_8754_01.mp4')
    cap = cv2.VideoCapture('tests/video/traffic_signs/IMG_8754_01.mp4')
    #cap = cv2.VideoCapture('tests/video/Demo1_1080.mp4')

    # Initialize traffic_control_flag which will be used to trigger voice. 
    # The traffic_control_name will be used when key:name mapping needed.
    traffic_control_flag = {"RedTrafficLight": False, "RedLeftTurnTrafficLight": False, "RedRightTurnTrafficLight": False, "StopTrafficSign": False, "StopAheadTrafficSign": False, "YieldTrafficSign": False, "YieldAheadTrafficSign": False, "SpeedLimitTrafficSign": False}
    traffic_control_flag_history = deque(maxlen=3)
    for _ in range(3):
        traffic_control_flag_history.appendleft(traffic_control_flag.copy())  
    traffic_control_name = {"RedTrafficLight": "red light", 
                    "RedLeftTurnTrafficLight": "red left turn light",
                    "RedRightTurnTrafficLight": "red right turn light",
                    "StopTrafficSign": "stop sign", 
                    "StopAheadTrafficSign": "stop ahead sign", 
                    "YieldTrafficSign": "yield sign", 
                    "YieldAheadTrafficSign": "yield ahead sign", 
                    "SpeedLimitTrafficSign": "speed limit sign"}
    last_voice_traffic_control_flag = {"RedTrafficLight": False, "RedLeftTurnTrafficLight": False, "RedRightTurnTrafficLight": False, "StopTrafficSign": False, "StopAheadTrafficSign": False, "YieldTrafficSign": False, "YieldAheadTrafficSign": False, "SpeedLimitTrafficSign": False}
    
    blinker_on = False

    reader = easyocr.Reader(['en'])

    #region
    last_speed_bbox = None
    last_speed_ocr_frame = -10**9
    # OCR_COOLDOWN = 3
    STABILITY_THRESHOLD = 0.5

    def is_bbox_stable(bbox1, bbox2):
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2

        inter_x1, inter_y1 = max(x1_min, x2_min), max(y1_min, y2_min)
        inter_x2, inter_y2 = min(x1_max, x2_max), min(y1_max, y2_max)

        inter_width = max(0, inter_x2 - inter_x1)
        inter_height = max(0, inter_y2 - inter_y1)

        inter_area = inter_width * inter_height

        if inter_area == 0:
            return 0.0

        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)

        return inter_area / (area1 + area2 - inter_area)
    #endregion

    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        
        if (count % PROCESS_EVERY_N== 0):        
            # Each iterate, reset current_traffic_control_flag and blinker_on for each frame
            current_traffic_control_flag = traffic_control_flag.copy()
            blinker_on = False

            # =================================
            # Function 1: Traffic Lights Detection via YOLO
            # stop, stopLeft, stopRight, go, goLeft, goRight, warning, warningLeft, warningRight
            # =================================

            # Detect traffic lights
            l_results = l_model(frame, imgsz=infer_imgsz, verbose=False)     
            l_class_names = l_model.names            
            #frame = l_results[0].plot(img=frame, line_width=2) 

            # For each traffic light
            for l_box in l_results[0].boxes:
                if l_box.conf[0] > l_conf_threshold:

                    # Extract details  
                    box_conf = l_box.conf[0].item()
                    x1, y1, x2, y2 = map(int, l_box.xyxy[0])
                    x, y, w, h = map(int, l_box.xywh[0])
                    box_id = int(l_box.cls[0].item())               
                    box_name = l_class_names[box_id]
                    #print(f"===========================Detected traffic light with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")
                
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness)
                    cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (255, 0, 0), thickness)
                    
                   
                    # crop traffic light image box
                    #new_x, new_y, new_w, new_h = int(x - w/2), int(y - h/2), int(w), int(h)
                    #cropped_traffic_light_frame = frame[new_y:new_y+new_h, new_x:new_x+new_w]
                    cropped_traffic_light_frame = crop_image(frame, (x - w/2, y - h/2, w, h))

                    
                    # Calculate the crop to original offsets
                    offset_x = int(x - w/2)
                    offset_y = int(y - h/2)
                    
                    cropped_traffic_light_frame = cv2.resize(cropped_traffic_light_frame, 
                                                # (width, height)
                                                (cropped_traffic_light_frame.shape[1], cropped_traffic_light_frame.shape[0]), 
                                                # cv2.INTER_CUBIC for better quality
                                                interpolation=cv2.INTER_CUBIC  
                                                )
                    

                    # Identify the bulb in the cropped image
                    b_results = b_model(cropped_traffic_light_frame, imgsz=bulb_infer_imgsz, verbose=False)
                    #cropped_traffic_light_frame = b_results[0].plot(line_width=1)  
                    #cv2.imshow("Cropped Frame", cropped_traffic_light_frame)   

                    b_class_names = b_model.names   
                    
                    # Initialize. Handle "forward bulb",  "left turn bulb", and "right turn bulb" separately
                    best_rgy_conf = {'red': 0, 'green': 0,  'yellow': 0}  
                    best_rgy_left_conf = {'red': 0, 'green': 0,  'yellow': 0}
                    best_rgy_right_conf = {'red': 0, 'green': 0,  'yellow': 0}
                    detected_rgy_boxes = {'red': [], 'green': [],  'yellow': []}  #"forward bulb"                                           
                    detected_rgy_left_boxes = {'red': [], 'green': [],  'yellow': []}  #"left turn bulb"   
                    detected_rgy_right_boxes = {'red': [], 'green': [],  'yellow': []}  #"right turn bulb" 

                    # Iterate through all detected traffic light bulbs, 
                    # append them to detected_rgy_boxes, detected_rgy_left_boxes and detected_rgy_right_boxes accordingly, 
                    # and update best_rgy_conf, best_rgy_left_conf, best_rgy_right_conf with the highest confidence scores
                    for b_box in b_results[0].boxes:
                        if b_box.conf[0] > b_conf_threshold:  
                            b_box_conf = b_box.conf[0].item()
                            b_box_id = int(b_box.cls[0].item())               
                            b_box_name = b_class_names[b_box_id]                      
                            match b_box_name.lower():
                                case "stop":
                                    if b_box_conf>best_rgy_conf['red']:
                                        best_rgy_conf['red'] = b_box_conf
                                    detected_rgy_boxes['red'].append(b_box)
                                case "stopleft":
                                    if b_box_conf>best_rgy_left_conf['red']:
                                        best_rgy_left_conf['red'] = b_box_conf
                                    detected_rgy_left_boxes['red'].append(b_box)
                                case "stopright":
                                    if b_box_conf>best_rgy_right_conf['red']:
                                        best_rgy_right_conf['red'] = b_box_conf
                                    detected_rgy_right_boxes['red'].append(b_box)
                                case "go":
                                    if b_box_conf>best_rgy_conf['green']:
                                        best_rgy_conf['green'] = b_box_conf
                                    detected_rgy_boxes['green'].append(b_box)
                                case "goleft":
                                    if b_box_conf>best_rgy_left_conf['green']:
                                        best_rgy_left_conf['green'] = b_box_conf
                                    detected_rgy_left_boxes['green'].append(b_box)
                                case "goright":
                                    if b_box_conf>best_rgy_right_conf['green']:
                                        best_rgy_right_conf['green'] = b_box_conf
                                    detected_rgy_right_boxes['green'].append(b_box)
                                case "warning":
                                    if b_box_conf>best_rgy_conf['yellow']:
                                        best_rgy_conf['yellow'] = b_box_conf 
                                    detected_rgy_boxes['yellow'].append(b_box)                              
                                case "warningleft":
                                    if b_box_conf>best_rgy_left_conf['yellow']:
                                        best_rgy_left_conf['yellow'] = b_box_conf
                                    detected_rgy_left_boxes['yellow'].append(b_box)
                                case "warningright":
                                    if b_box_conf>best_rgy_right_conf['yellow']:
                                        best_rgy_right_conf['yellow'] = b_box_conf
                                    detected_rgy_right_boxes['yellow'].append(b_box)      

                    # for color, conf in best_rgy_conf.items():
                    #     print(f"===========================Detected {color} bulb with {conf:.2f} confidence")
                    # for color, conf in best_rgy_left_conf.items():
                    #     print(f"===========================Detected {color} left turn bulb with {conf:.2f} confidence")
                    # for color, conf in best_rgy_right_conf.items():
                    #     print(f"===========================Detected {color} right turn bulb with {conf:.2f} confidence")
                    
                
                    # Will be used to store all bulb boxes which will be plotted
                    plot_boxes = []

                    # Determine the dominant color of the "forward bulb", since only one of red, yellow, or green can be active at a time. 
                    # Then, add all forward bulbs of the dominant color to plot_boxes. 
                    # If the dominant color is red, set current_traffic_control_flag['RedTrafficLight'] to True.
                    for key, value in best_rgy_conf.items():
                        if all(value >= other_val + diff_conf for other_k, other_val in best_rgy_conf.items() if other_k != key): 
                            if key=="red":
                                current_traffic_control_flag["RedTrafficLight"] = True
                            plot_boxes.extend(detected_rgy_boxes[key])     

                    # Apply the same logic to handle the "left turn bulb".
                    for key, value in best_rgy_left_conf.items():
                        if all(value >= other_val + diff_conf for other_k, other_val in best_rgy_left_conf.items() if other_k != key):
                            if key=="red":
                                current_traffic_control_flag["RedLeftTurnTrafficLight"] = True
                            plot_boxes.extend(detected_rgy_left_boxes[key])   

                    # Apply the same logic to handle the "right turn bulb".
                    for key, value in best_rgy_right_conf.items():
                        if all(value >= other_val + diff_conf for other_k, other_val in best_rgy_right_conf.items() if other_k != key):
                            if key=="red":
                                current_traffic_control_flag["RedRightTurnTrafficLight"] = True
                            plot_boxes.extend(detected_rgy_right_boxes[key])      

                    # Plot all boxes in plot_boxes
                    for plot_box in plot_boxes:
                        #p_box_conf = plot_box.conf[0].item()
                        p_x1, p_y1, p_x2, p_y2 = map(int, plot_box.xyxy[0])
                        #p_x, p_y, p_w, p_h = map(int, plot_box.xywh[0])
                        p_box_id = int(plot_box.cls[0].item())               
                        p_box_name = b_class_names[p_box_id]  
                        

                        p_x1 = int(p_x1 + offset_x)
                        p_y1 = int(p_y1 + offset_y)
                        p_x2 = int(p_x2 + offset_x)
                        p_y2 = int(p_y2 + offset_y)

                        match p_box_name:
                            case "stop":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 0, 255), thickness)
                                cv2.putText(frame, '', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 0, 255), thickness) 
                            case "stopLeft":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 0, 255), thickness)
                                cv2.putText(frame, 'left', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 0, 255), thickness)
                            case "stopRight":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 0, 255), thickness)
                                cv2.putText(frame, 'right', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 0, 255), thickness)
                            case "go":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 0), thickness)
                                cv2.putText(frame, '', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
                            case "goLeft":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 0), thickness)
                                cv2.putText(frame, 'left', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
                            case "goRight":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 0), thickness)
                                cv2.putText(frame, 'right', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
                            case "warning":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 255), thickness)
                                cv2.putText(frame, '', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness)                           
                            case "warningLeft":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 255), thickness)
                                cv2.putText(frame, 'left', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness) 
                            case "warningRight":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 255), thickness)
                                cv2.putText(frame, 'right', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness)     
                            

            # =====================================
            # Function 2: Traffic Signs Detection via YOLO
            # stop, stopAhead, yield, yieldAhead, speedLimit
            # ======================================

            # Detect traffic signs
            s_results = s_model(frame, imgsz=infer_imgsz, verbose=False)             
            s_class_names = s_model.names
            #frame = s_results[0].plot(img=frame, line_width=2) 
            
            # Loop each box to find "stop", "stopAhead", "yield", "yieldAhead" signs and speed limit signs
            best_speed_limit_value = 1000
            best_speed_limit_conf = 0
            for s_box in s_results[0].boxes:
                if s_box.conf[0] > s_conf_threshold:
                    box_conf = s_box.conf[0].item()
                    x1, y1, x2, y2 = map(int, s_box.xyxy[0])
                    x, y, w, h = map(int, s_box.xywh[0])
                    box_id = int(s_box.cls[0].item())               
                    box_name = s_class_names[box_id]

                    #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                    #cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10),
                    #    cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (0, 0, 255), thickness)
                    
                    # Check stop , stop ahead, yield, and yield ahead
                    if box_name in ["stop", "stopAhead", "yield", "yieldAhead"]:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                        cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (0, 0, 255), thickness)   
                        #print(f"===========================Detected {box_name} with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")                                   
                        match box_name:
                            case "stop":
                                current_traffic_control_flag["StopTrafficSign"]=True
                            case "stopAhead":
                                current_traffic_control_flag["StopAheadTrafficSign"]=True
                            case "yield":
                                current_traffic_control_flag["YieldTrafficSign"]=True
                            case "yieldAhead":
                                current_traffic_control_flag["YieldAheadTrafficSign"]=True                    
                    # Speed Limit Signs
                    else: 
                        #print(f"===========================Detected {box_name} with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")                                                         
                        cropped = frame[y1:y2, x1:x2]
                        target_words = ['speed', 'limit']
                        found_targets = {target: False for target in target_words}

                        # Call EasyOCR 
                        box = (x1, y1, x2, y2)
                        # do_ocr = True

                        #region
                        do_ocr = False
                        if last_speed_bbox is not None and is_bbox_stable(last_speed_bbox, box) >= STABILITY_THRESHOLD:
                             do_ocr = (count - last_speed_ocr_frame) >= OCR_COOLDOWN_FRAMES
                        else:
                             do_ocr = (count - last_speed_ocr_frame) >= OCR_COOLDOWN_FRAMES
                        #endregion

                        if do_ocr:
                            last_speed_bbox = box
                            last_speed_ocr_frame = count
                            results = reader.readtext(cropped)
                            all_lowercase_text = ' '.join([text for (_, text, _) in results]).lower()
                            #print(f"===========================Extracted sign words using EasyOcr: {all_lowercase_text}")
                            for _, text, _ in results:
                                for target in target_words:
                                    if not found_targets[target] and fuzz.ratio(text.lower(), target) > 0.8:
                                        found_targets[target] = True 


                            # Check if both 'speed' and 'limit' are found   
                            if found_targets['speed'] and found_targets['limit']:                                                                       
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness)
                                cv2.putText(frame, f'speedLimit {box_conf:.2f}', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (255, 0, 0), thickness)
                                current_traffic_control_flag["SpeedLimitTrafficSign"]=True

                                match = re.search(r'\b\d{1,2}\b', all_lowercase_text)
                                if match:
                                    speed_limit_value = int(match.group())                                
                                    if box_conf >= best_speed_limit_conf:                    
                                        best_speed_limit_conf = s_box.conf[0].item()
                                        best_speed_limit_value = speed_limit_value
                                    #print(f"===========================Extracted speed limit sign value: {speed_limit_value}")  


            
            # gps.update()
            # global last_print
            # current = time.monotonic()
            # if current - last_print >= 1.0:
            #     last_print = current
            #     if not gps.has_fix:
            #         print('===========================GPS Waiting for fix...')
            #     else:
            #         print('===========================GPS shows Latitude: {0:.6f} degrees'.format(gps.latitude))
            #         print('===========================GPS shows Longitude: {0:.6f} degrees'.format(gps.longitude))

            #         # Get the speed
            #         if gps.speed_knots is not None:
            #             driving_mph = gps.speed_knots * 1.15078
            #             print('===========================Driving Speed: {0:.2f} mph'.format(driving_mph))
            #             # Check if the speed exceeds the limit
            #             if driving_mph > best_speed_limit_value:
            #                speak_queued("Slow down!")
            #         else:
            #             print('===========================Driving speed is not available')

            

            # =====================================
            # Turning Signal Detection via IMU sensor and microphone
            # ==========================================
            # detected_turn = detect_turn()
            # print(f"===========================Detected Turn: {detected_turn}")
            # if not blinker_on and detected_turn != "Straight":
            #     speak_queued(f"Don't forget to turn on your turn signal when turning!")
                       

            # =======================================
            # Trigger Voice Feedback Based on Analysis
            # ========================================      
            # Voice triggered when the following traffic signal detected or undetected
            # 1. traffic light: red light, red left turn light, and red right turn light 
            # 2. traffic sign: stop , stop ahead, yield, yield ahead, and speed limit when speeding
            traffic_control_flag_history.appendleft(current_traffic_control_flag)
            #print([traffic_control_flag_history[i]["SpeedLimitTrafficSign"] for i in range(len(traffic_control_flag_history))])
            #print(last_voice_traffic_control_flag["SpeedLimitTrafficSign"])


            splitter = ", "
            voice_text_for_detection = ""
            voice_text_for_not_detection = ""
            voice_speed_limit_text_for_detection = ""
            voice_text=""
            for key in current_traffic_control_flag:
                # If traffic control has been detected for three times in a row and previous status is not detected.            
                if (traffic_control_flag_history[0][key] 
                    and all(traffic_control_flag_history[0][key] == traffic_control_flag_history[i][key] for i in range(1, 3))
                    and not last_voice_traffic_control_flag[key]
                    ):
                    if key == "SpeedLimitTrafficSign":
                        # For demo only
                        driving_mph = random.randint(best_speed_limit_value, best_speed_limit_value+5)

                        if driving_mph > best_speed_limit_value:
                            #speak_queued(f"{traffic_control_name[key]} detected. The speed limit is {best_speed_limit_value}. Your current speed is {driving_mph}. Please slow down.") 
                            #print(f"==========================={traffic_control_name[key]} detected. The speed limit is {best_speed_limit_value}. Your speed is {driving_mph}. Please slow down.")                            
                            voice_speed_limit_text_for_detection = f"{traffic_control_name[key]} detected. The speed limit is {best_speed_limit_value}. Your speed is {driving_mph}. Please slow down. "

                    else:
                        #speak_queued(f"{traffic_control_name[key]} detected. Please slow down")  
                        #print(f"==========================={traffic_control_name[key]} detected. Please slow down") 
                        voice_text_for_detection = voice_text_for_detection + splitter + traffic_control_name[key]
                    
                    last_voice_traffic_control_flag[key] = traffic_control_flag_history[0][key]
                                     
                # If traffic control has not been detected for three times in a row and previous status is detected.  
                if (not traffic_control_flag_history[0][key] 
                    and all(traffic_control_flag_history[0][key] == traffic_control_flag_history[i][key] for i in range(1, 3))
                    and last_voice_traffic_control_flag[key]
                    ):             
                    if key != "SpeedLimitTrafficSign":
                        #speak_queued(f"{traffic_control_name[key]} no longer detected.")
                        #print(f"==========================={traffic_control_name[key]} no longer detected.")
                        voice_text_for_not_detection = voice_text_for_not_detection + splitter + traffic_control_name[key]
                    
                    last_voice_traffic_control_flag[key] = traffic_control_flag_history[0][key]

            voice_text_for_detection = f"{voice_text_for_detection[2:]} detected. Please slow down." if voice_text_for_detection else ""
            voice_text_for_not_detection = f"{voice_text_for_not_detection[2:]} no longer detected." if voice_text_for_not_detection else ""
            voice_text = " ".join(filter(None, [voice_text_for_detection, voice_speed_limit_text_for_detection, voice_text_for_not_detection]))
            if voice_text!="":
                #speak_queued(voice_text) 
                print(voice_text)

            # Set up a named window with full-screen support
            cv2.namedWindow("Annotated Frame", cv2.WND_PROP_FULLSCREEN)
            # Make it full screen
            # cv2.setWindowProperty("Annotated Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Annotated Frame", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # if (count % 10 == 0):
            #     # Small delay to ease CPU load
            #     sleep(0.17) 
            #     #sleep(1.00)  

    cap.release()
    cv2.destroyAllWindows()
    
    end_time = datetime.now()
    duration = end_time - start_time
    print("Duration:", duration)

if __name__ == "__main__":
    main()