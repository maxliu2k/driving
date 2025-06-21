# Voting System between frames to improve accuracy
# 1. Red light detection Example: if, in the last 3 frames, the red light was detected more than 50% of the time, then consider it as detected.

#========#from voice import Voice
import cv2
from ultralytics import YOLO
from utils import *
#========#import smbus
from time import sleep
import math
import threading
import pytesseract
#pip install rapidfuzz
from rapidfuzz import fuzz
#pip install easyocr
import easyocr
import re
#========#import serial
#========#import adafruit_gps
import time
from collections import deque
# import pynmea2 #pip install pyserial pynmea2




"""
def speak_async(voice, text):
    threading.Thread(target=voice.speak, args=(text,), daemon=True).start()

# ===== GPS Setup =====

uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=30)

gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

gps.send_command(b'PMTK220,1000')

last_print = time.monotonic()



# =============================== 
# Accelerometer (MPU6050) Setup
# ===============================
# Accelerometer Registers
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

# For Raspberry Pi
bus = smbus.SMBus(1)     

# MPU6050 device address
Device_Address = 0x68

# Offsets provided for calibration
Ax_offset = 0.05
Ay_offset = -0.01
Az_offset = -1.11
Gx_offset = 0.29
Gy_offset = 0.07
Gz_offset = 0.09

# Filtering and Thresholds
GYRO_WINDOW = 10
GYRO_THRESHOLD = 5.0 # degrees/sec

# Deques for storing gyro data
gyro_buffer = deque(maxlen=GYRO_WINDOW)

def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value = value - 65536
    return value

def get_motion_data():
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)
    
    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0
    Gx = gyro_x / 131.0
    Gy = gyro_y / 131.0
    Gz = gyro_z / 131.0
    
    return Ax, Ay, Az, Gx, Gy, Gz

def get_direction_and_acceleration():
    Ax, Ay, Az, Gx, Gy, Gz = get_motion_data()
    accel_magnitude = math.sqrt(Ax**2 + Ay**2 + Az**2)
    
    # Simple directional estimation using Ax and Ay
    if Ax > 0.5:
        direction = "Right"
    elif Ax < -0.5:
        direction = "Left"
    elif Ay > 0.5:
        direction = "Forward"
    elif Ay < -0.5:
        direction = "Backward"
    else:
        direction = "Stationary"
    
    return direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz

def detect_turn():

    #Design Notes:
    #- sometimes the road can have bumps so we might need a filter
    #- primarily rely on gyro (yaw rate) to detect turns
    #    - either y or z axis, tbd

    _, _, _, Gx, Gy, Gz = get_motion_data()
    gyro_buffer.append(Gy)

    # Compute moving average
    gyro_avg = sum(gyro_buffer) / len(gyro_buffer)

    # Determine the turn:
    if abs(gyro_avg) > GYRO_THRESHOLD:
        if gyro_avg > 0:
            return "Right Turn"
        else:
            return "Left Turn"
    else:
        return "Straight"


# def read_gps_speed(serial_port='/dev/serial0', baudrate=9600):
#     # Open serial connection to GPS
#     speed_mph = 0
#     with serial.Serial(serial_port, baudrate, timeout=1) as ser:
#         while True:
#             try:
#                 line = ser.readline().decode('ascii', errors='replace')
#                 if line.startswith('$GPRMC'):
#                     msg = pynmea2.parse(line)
#                     if msg.status == 'A':  # A = valid, V = invalid
#                         speed_knots = float(msg.spd_over_grnd)
#                         speed_mph = speed_knots * 1.15078
#             except pynmea2.ParseError:
#                 continue
#     return speed_mph

"""

# ========================================
# Main function integrating vision and IMU
# ========================================

def main():

    # Voting Queue to store the last 3 frames
    voting_queue = []
    voting_queue_size = 3
    voting_required_percentage = 0.5

    l_conf_threshold=0.5 #Traffic light confidence threshold value
    b_conf_threshold=0.5 #Traffic light bulb confidence threshold value
    s_conf_threshold=0.4 #Traffic sign confidence threshold value

    diff_conf = 0.1  #To be used to find dominant color of traffic bulb
    big_font_scale = 0.6  #To be used when plot 
    small_font_scale = 0.4  #To be used when plot 
    thickness = 2 #To be used when plot 
    fuzzy_threshold = 80  #To be used when compare words retrieved from traffic sign with keyword "speed"/"limit"
    driving_speed=0

    #========#voice = Voice("piper.onnx")
    count = 0

    # Load YOLO model
    l_model = YOLO('bestlights.pt')
    b_model = YOLO('bestbulbs.pt')
    s_model = YOLO('bestsigns.pt') 

    # Start video stream
    #cap = cv2.VideoCapture(0)
    # alternatively, use a video file 
    cap = cv2.VideoCapture('videoTest/TrafficLights/IMG_8754_01.mp4')
    #cap = cv2.VideoCapture('videoTest/TrafficSigns/IMG_8754_01.mp4')
    #========#voice.speak("Recording started!")

    # Initialize traffic_control_flag and last_traffic_control_flag, which will be used to trigger voice. 
    # The traffic_control_name will be used when key:name mapping needed.
    last_traffic_control_flag = {"RedTrafficLight": False, "RedLeftTrafficLight": False, "StopTrafficSign": False, "StopAheadTrafficSign": False, "YieldTrafficSign": False, "YieldAheadTrafficSign": False, "SpeedLimitTrafficSign": False}
    traffic_control_flag = {"RedTrafficLight": False, "RedLeftTrafficLight": False, "StopTrafficSign": False, "StopAheadTrafficSign": False, "YieldTrafficSign": False, "YieldAheadTrafficSign": False, "SpeedLimitTrafficSign": False}
    traffic_control_name = {"RedTrafficLight": "red traffic light", 
                    "RedLeftTrafficLight": "red left traffic light",
                    "StopTrafficSign": "stop traffic sign", 
                    "StopAheadTrafficSign": "stop ahead traffic sign", 
                    "YieldTrafficSign": "yield traffic sign", 
                    "YieldAheadTrafficSign": "yield ahead traffic sign", 
                    "SpeedLimitTrafficSign": "speed limit traffic sign"}
    
    
    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break

        if (count % 30 == 0):          

            # Result ID require values:
            # 1. Red/Green light
            # 2. Stop sign
            # 3. * Speed limit sign
            # Scenario1: Driving up to intersection where there are three lights, currently all green
            # Example (error included): R0 for current frame, but the last two were G0 and G0 so still green            
            # Scenario2: Driving up to intersection where there are three lights, currently all red
            result_id = ""

            # Each iterate, reset traffic_control_flag for each frame
            for key in traffic_control_flag:
                traffic_control_flag[key] = False

            # =================================
            # Function 1: Traffic Lights Detection via YOLO
            # go, goLeft, stop, stopLeft, warning, warningLeft
            # =================================

            # Detect traffic lights
            l_results = l_model(frame)   
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
                    print(f"===========================Detected traffic light with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")
                
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness)
                    cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (255, 0, 0), thickness)
                    
                    # crop the image to the traffic light
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
                    b_results = b_model(cropped_traffic_light_frame)
                    #cropped_traffic_light_frame = b_results[0].plot(line_width=1)  
                    #cv2.imshow("Cropped Frame", cropped_traffic_light_frame)   

                    b_class_names = b_model.names   
                    
                    # Initialize. Handle "forward light bulb" and "left light bulb" separately
                    best_rgy_conf = {'red': 0, 'green': 0,  'yellow': 0}  
                    best_rgy_left_conf = {'red': 0, 'green': 0,  'yellow': 0}
                    detected_rgy_boxes = {'red': [], 'green': [],  'yellow': []}  #"forward light bulb"                                           
                    detected_rgy_left_boxes = {'red': [], 'green': [],  'yellow': []}  #"left light bulb"    

                    # Iterate through all detected traffic light bulbs, 
                    # append them to detected_rgy_boxes/detected_rgy_left_boxes accordingly, 
                    # and update best_rgy_conf/best_rgy_left_conf with the highest confidence scores
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
                                case "go":
                                    if b_box_conf>best_rgy_conf['green']:
                                        best_rgy_conf['green'] = b_box_conf
                                    detected_rgy_boxes['green'].append(b_box)
                                case "goleft":
                                    if b_box_conf>best_rgy_left_conf['green']:
                                        best_rgy_left_conf['green'] = b_box_conf
                                    detected_rgy_left_boxes['green'].append(b_box)
                                case "warning":
                                    if b_box_conf>best_rgy_conf['yellow']:
                                        best_rgy_conf['yellow'] = b_box_conf 
                                    detected_rgy_boxes['yellow'].append(b_box)                              
                                case "warningleft":
                                    if b_box_conf>best_rgy_left_conf['yellow']:
                                        best_rgy_left_conf['yellow'] = b_box_conf
                                    detected_rgy_left_boxes['yellow'].append(b_box)       

                    #for color, conf in best_rgy_conf.items():
                    #    print(f"===========================Detected traffic {color} bulb with {conf:.2f} confidence")
                    #for color, conf in best_rgy_left_conf.items():
                    #    print(f"===========================Detected traffic {color} left bulb with {conf:.2f} confidence")
                    
                    # Will be used to Store all bulb boxes which will be plotted
                    plot_boxes = []

                    # Determine the dominant color of the "forward light bulb", since only one of red, yellow, or green can be active at a time. 
                    # Then, add all forward bulbs of the dominant color to plot_boxes. 
                    # If the dominant color is red, set traffic_control_flag['RedTrafficLight'] to True.
                    for key, value in best_rgy_conf.items():
                        if all(value >= other_val + diff_conf for other_k, other_val in best_rgy_conf.items() if other_k != key): 
                            if key=="red" and result_id == "":
                                traffic_control_flag["RedTrafficLight"] = True
                                result_id="R"
                            plot_boxes.extend(detected_rgy_boxes[key])     

                    # Apply the same logic to handle the "left light bulb".
                    for key, value in best_rgy_left_conf.items():
                        if all(value >= other_val + diff_conf for other_k, other_val in best_rgy_left_conf.items() if other_k != key):
                            if key=="red" and result_id == "":
                                traffic_control_flag["RedLeftTrafficLight"] = True
                                result_id="R"
                            plot_boxes.extend(detected_rgy_left_boxes[key])        

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
                            case "go":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 0), thickness)
                                cv2.putText(frame, '', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
                            case "goLeft":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 0), thickness)
                                cv2.putText(frame, 'left', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
                            case "warning":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 255), thickness)
                                cv2.putText(frame, '', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness)                           
                            case "warningLeft":
                                cv2.rectangle(frame, (p_x1, p_y1), (p_x2, p_y2), (0, 255, 255), thickness)
                                cv2.putText(frame, 'left', (int(p_x2), int(p_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness)     
                            

            # =====================================
            # Function 2: Traffic Signs Detection via YOLO
            # stop/stopAhead Signs
            # Speed Limit Sign: Passive Reminding using GPS sensor
            # ======================================

            # Detect traffic signs
            s_results = s_model(frame)             
            s_class_names = s_model.names
            #frame = s_results[0].plot(img=frame, line_width=2) 

            # Loop each box to find "stop", "stopAhead", "yield", "yieldAhead" signs and speed limit signs
            best_speed_limit_value = 0
            best_speed_limit_conf = 0
            for s_box in s_results[0].boxes:
                if s_box.conf[0] > s_conf_threshold:
                    box_conf = s_box.conf[0].item()
                    x1, y1, x2, y2 = map(int, s_box.xyxy[0])
                    x, y, w, h = map(int, s_box.xywh[0])
                    box_id = int(s_box.cls[0].item())               
                    box_name = s_class_names[box_id]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                    cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (0, 0, 255), thickness)
                    
                    # "stop", "stopAhead", "yield", "yieldAhead" signs
                    if box_name in ["stop", "stopAhead", "yield", "yieldAhead"]:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                        cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (0, 0, 255), thickness)   
                        print(f"===========================Detected {box_name} with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")                                   
                        match box_name:
                            case "stop":
                                traffic_control_flag["StopTrafficSign"]=True
                            case "stopAhead":
                                traffic_control_flag["StopAheadTrafficSign"]=True
                            case "yield":
                                traffic_control_flag["YieldTrafficSign"]=True
                            case "yieldAhead":
                                traffic_control_flag["YieldAheadTrafficSign"]=True

                    
                    # Speed Limit Signs
                    else: 
                        print(f"===========================Detected {box_name} with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")                                   
                        
                        # Crop the detected region from the frame
                        cropped = frame[y1:y2, x1:x2]

                        # Save the cropped image for debugging
                        #cv2.imwrite(f"cropped_speed_limit_sign_{count}.jpg", cropped)

                        #1. Try pytesseract first
                        #gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                        #gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
                        #_, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
                        #processed = cv2.medianBlur(thresh, 3)
                        #config = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                        #all_lowercase_text = pytesseract.image_to_string(cropped, config=config).lower()
                        #print(f"===========================Extracted sign words using pytesseract: {all_lowercase_text}")   
                        #Use fuzz match to find "speed" and "limit" keyword"
                        #words = all_lowercase_text.split()                                              
                        #target_words = ['speed', 'limit']
                        #found_targets = {target: False for target in target_words}
                        # Check each word in OCR result against each target word
                        #for word in words:
                        #    for target in target_words:
                        #        if not found_targets[target] and fuzz.ratio(word, target) > 0.8:
                        #            found_targets[target] = True                   
                        #2. Then try easyocr if pytesseract does not work
                        #if not found_targets['speed'] or not found_targets['limit']:   
                            
                        reader = easyocr.Reader(['en'])
                        results = reader.readtext(cropped)
                        all_lowercase_text = ' '.join([text for (_, text, _) in results]).lower()
                        print(f"===========================Extracted sign words using EasyOcr: {all_lowercase_text}")
                        #if 'speed' in all_lowercase_text:
                        #   found_targets['speed'] = True
                        #if 'limit' in all_lowercase_text:
                        #    found_targets['limit'] = True

                        #if found_targets['speed'] and found_targets['limit']:     
                        if 'speed' in all_lowercase_text and 'limit' in all_lowercase_text:                                                                          
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness)
                            cv2.putText(frame, f'speedLimit {box_conf:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (255, 0, 0), thickness)
                            traffic_control_flag["SpeedLimitTrafficSign"]=True

                            match = re.search(r'\b\d{1,2}\b', all_lowercase_text)
                            if match:
                                speed_limit_value = int(match.group())                                
                                if box_conf >= best_speed_limit_conf:                    
                                    best_speed_limit_conf = s_box.conf[0].item()
                                    best_speed_limit_value = speed_limit_value
                                print(f"===========================Extracted speed limit sign value: {speed_limit_value}")  
                            
                                  
                        
            """
            gps.update()
            current = time.monotonic()
            if current - last_print >= 1.0:
                last_print = current
                if not gps.has_fix:
                    print('===========================GPS Waiting for fix...')
                else:
                    print('===========================GPS shows Latitude: {0:.6f} degrees'.format(gps.latitude))
                    print('===========================GPS shows Longitude: {0:.6f} degrees'.format(gps.longitude))

                    # Get the speed
                    if gps.speed_knots is not None:
                        driving_mph = gps.speed_knots * 1.15078
                        print('===========================Driving Speed: {0:.2f} mph'.format(driving_mph))

                        # Check if the speed exceeds the limit
                        #if driving_mph > best_speed_limit_value:
                        #    voice.speak("Slow down!")
                    else:
                        print('===========================Driving speed is not available')
            """

            # =====================================
            # Function 3: Turning Signal Detection via accelerometer sensor and microphone
            # ==========================================
  
            # Get accelerometer data
            # direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz = get_direction_and_acceleration()
            # print(f"Accel -> Direction: {direction}, Accel: {accel_magnitude:.2f}, "
            #     f"Ax: {(Ax+Ax_offset):.2f}, Ay: {(Ay+Ay_offset):.2f}, Az: {(Az+Az_offset):.2f}")
            # Example: if moving forward with high acceleration (indicating speeding), warn to slow down
            """
            detected_turn = detect_turn()
            print(f"Detected Turn: {detected_turn}")
            if not blinker_on and detected_turn != "Straight":
                voice.speak(f"Don't forget to turn on your turn signal when turning!")
            """
            # if direction == "Forward" and accel_magnitude > 1.5:
            #     voice.speak("Slow down!")
            

            # =====================================
            # Function 4: Seat Belt (Optional)
            # ==========================================

            

            # =======================================
            # Trigger Voice Feedback Based on Analysis
            # ========================================

            """
            # Voice triggered when the following traffic control detected or undetected
            # 1. traffic light: red trafic light, red left traffic light 
            # 2. traffic sign: 'stop traffic sign', 'stop ahead traffic sign', 'yield traffic sign', 'yield ahead traffic sign', 'speed limit traffic sign'
            for key in traffic_control_flag:
                #if traffic control detected this time, but not last time             
                if (traffic_control_flag[key] and not last_traffic_control_flag[key]):
                    if key == "speedLimit":
                        if driving_mph > best_speed_limit_value:
                            speak_async(voice, f"{traffic_control_name[key]} detected. The speed limit is {best_speed_limit_value}. Your current speed is {driving_mph}. Please slow down.")    
                        else:
                            speak_async(voice, f"{traffic_control_name[key]} detected.")
                    else:
                        speak_async(voice, f"{traffic_control_name[key]} detected. Please slow down")               
                #if traffic control not detected this time, but detected last time 
                if (not traffic_control_flag[key] and last_traffic_control_flag[key]):
                    speak_async(voice, f"{traffic_control_name[key]} no longer detected.")

                last_traffic_control_flag[key] = traffic_control_flag[key]
            """

            #sets up a named window with full-screen support
            cv2.namedWindow("Annotated Frame", cv2.WND_PROP_FULLSCREEN)
            #actually makes it full screen
            cv2.setWindowProperty("Annotated Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Annotated Frame", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # if (count % 5 == 0):
            #     # Small delay to ease CPU load
            #     sleep(0.17)  

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()