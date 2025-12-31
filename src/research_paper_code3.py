import cv2
from ultralytics import YOLO
import threading
import random
from datetime import datetime
from time import sleep
import queue
from collections import deque

import easyocr
from rapidfuzz import fuzz
import re

import smbus
from collections import deque

import time
import serial
import adafruit_gps

import io
import sys
import wave
import subprocess
from piper import PiperVoice
import threading
import queue
#from playsound import playsound

import argparse, time, os
from pathlib import Path
from typing import Tuple, List, Optional, Callable
import numpy
import torchaudio #pip install torchaudio==2.4.1
import sounddevice
from utils import *
from small_audio_cnn import SmallAudioCNN
from speed_limit_OCR import SpeedLimitOCR
from GPS_controller import GPSController
from IMU_controller import IMUController
from voice_playback_manager import VoicePlaybackManager
from turn_signal_detection_manager import TurnSignalDetectionManager

# Optional decoders for files
try:
    import soundfile #pip install soundfile
    _HAVE_SF = True
except Exception:
    _HAVE_SF = False
try:
    from pydub import AudioSegment
    _HAVE_PYDUB = True
except Exception:
    _HAVE_PYDUB = False


# Process a single detected traffic light box and update confidence values and detected box lists for each color and direction
def process_rgy_box(
    b_box, b_box_conf, b_box_name,
    best_rgy_conf, best_rgy_left_conf, best_rgy_right_conf,
    detected_rgy_boxes, detected_rgy_left_boxes, detected_rgy_right_boxes
):
    match b_box_name:
        case "stop":
            if b_box_conf > best_rgy_conf['red']:
                best_rgy_conf['red'] = b_box_conf
            detected_rgy_boxes['red'].append((b_box, b_box_name))

        case "stopLeft":
            if b_box_conf > best_rgy_left_conf['red']:
                best_rgy_left_conf['red'] = b_box_conf
            detected_rgy_left_boxes['red'].append((b_box, b_box_name))

        case "stopRight":
            if b_box_conf > best_rgy_right_conf['red']:
                best_rgy_right_conf['red'] = b_box_conf
            detected_rgy_right_boxes['red'].append((b_box, b_box_name))

        case "go":
            if b_box_conf > best_rgy_conf['green']:
                best_rgy_conf['green'] = b_box_conf
            detected_rgy_boxes['green'].append((b_box, b_box_name))

        case "goLeft":
            if b_box_conf > best_rgy_left_conf['green']:
                best_rgy_left_conf['green'] = b_box_conf
            detected_rgy_left_boxes['green'].append((b_box, b_box_name))

        case "goRight":
            if b_box_conf > best_rgy_right_conf['green']:
                best_rgy_right_conf['green'] = b_box_conf
            detected_rgy_right_boxes['green'].append((b_box, b_box_name))

        case "warning":
            if b_box_conf > best_rgy_conf['yellow']:
                best_rgy_conf['yellow'] = b_box_conf
            detected_rgy_boxes['yellow'].append((b_box, b_box_name))

        case "warningLeft":
            if b_box_conf > best_rgy_left_conf['yellow']:
                best_rgy_left_conf['yellow'] = b_box_conf
            detected_rgy_left_boxes['yellow'].append((b_box, b_box_name))

        case "warningRight":
            if b_box_conf > best_rgy_right_conf['yellow']:
                best_rgy_right_conf['yellow'] = b_box_conf
            detected_rgy_right_boxes['yellow'].append((b_box, b_box_name))


# Determine the dominant color for forward, left, and right directions
def get_dominant_color_for_direction(
    best_rgy_conf, best_rgy_left_conf, best_rgy_right_conf,
    detected_rgy_boxes, detected_rgy_left_boxes, detected_rgy_right_boxes,
    diff_conf):

    dominant_color_box_list = []  # single list of tuples: (box, box_name)
    dominant_color = {}

    def process_conf(best_conf, detected_boxes, direction):
        for color, conf_value in best_conf.items():
            if all(conf_value >= other_val + diff_conf
                   for other_color, other_val in best_conf.items() if other_color != color):
                dominant_color[direction] = color
                dominant_color_box_list.extend(detected_boxes[color])
                # for box in detected_boxes[color]:
                #     box_id = int(box.cls[0].item())
                #     box_name = b_class_names[box_id].lower()
                #     dominant_color_box_list.append((box, box_name))

    process_conf(best_rgy_conf, detected_rgy_boxes, "forward")
    process_conf(best_rgy_left_conf, detected_rgy_left_boxes, "left")
    process_conf(best_rgy_right_conf, detected_rgy_right_boxes, "right")

    return dominant_color, dominant_color_box_list

# Analyze all detected traffic light boxes to determine the dominant color
#(red, yellow, green) for forward, left-turn, and right-turn directions.
def analyze_light_bulbs(b_results, b_class_names, b_conf_threshold, diff_conf):

    # Initialize confidence and box containers
    conf = {
        "forward": {'red': 0, 'yellow': 0, 'green': 0},
        "left":    {'red': 0, 'yellow': 0, 'green': 0},
        "right":   {'red': 0, 'yellow': 0, 'green': 0},
    }
    boxes = {
        "forward": {'red': [], 'yellow': [], 'green': []},
        "left":    {'red': [], 'yellow': [], 'green': []},
        "right":   {'red': [], 'yellow': [], 'green': []},
    }

    # Map class names to direction and color
    mapping = {
        "stop": ("forward", "red"),
        "stopLeft": ("left", "red"),
        "stopRight": ("right", "red"),
        "warning": ("forward", "yellow"),
        "warningLeft": ("left", "yellow"),
        "warningRight": ("right", "yellow"),
        "go": ("forward", "green"),
        "goLeft": ("left", "green"),
        "goRight": ("right", "green"),
    }

    # Process all detected boxes
    for b_box in b_results[0].boxes:
        b_conf = b_box.conf[0].item()
        if b_conf < b_conf_threshold:
            continue

        b_name = b_class_names[int(b_box.cls[0].item())]
        if b_name not in mapping:
            continue  # skip unknown labels

        direction, color = mapping[b_name]
        boxes[direction][color].append((b_box, b_name))

        # Update best confidence
        if b_conf > conf[direction][color]:
            conf[direction][color] = b_conf

    # Determine dominant colors
    dominant_color = {}
    dominant_color_box_list = []

    for direction, color_conf in conf.items():
        for color, val in color_conf.items():
            if all(val >= other_val + diff_conf
                   for other_color, other_val in color_conf.items() if other_color != color):
                dominant_color[direction] = color
                dominant_color_box_list.extend(boxes[direction][color])

    return dominant_color, dominant_color_box_list


# ========================================
# Main function
# ========================================
def main():

    imu_controller = IMUController()
    gps_controller = GPSController()
    turn_signal_detection_manager = TurnSignalDetectionManager("models/sound/turn_signal_cnn.pt", "cpu")
    voice_playback_manager = VoicePlaybackManager("models/voice/piper.onnx")
  
    print("===========================Starting turn signal detection engine...")
    turn_signal_detection_manager.start()

    print("===========================Starting voice playback engine...")    
    voice_playback_manager.start()

    # Initialize traffic lights and signs to false
    traffic_control_flag = {
        "RedTrafficLight": False, 
        "RedLeftTurnTrafficLight": False, 
        "RedRightTurnTrafficLight": False, 
        "StopTrafficSign": False, 
        "StopAheadTrafficSign": False, 
        "YieldTrafficSign": False, 
        "YieldAheadTrafficSign": False, 
        "SpeedLimitTrafficSign": False}
    
    traffic_control_flag_history = deque(maxlen=3)
    for _ in range(3):
        traffic_control_flag_history.append(traffic_control_flag.copy())  

    last_confirmed_traffic_control_flag = traffic_control_flag.copy()
    
    # Load YOLO models
    l_model = YOLO('models/image/best_light.pt')
    b_model = YOLO('models/image/best_bulb.pt')
    s_model = YOLO('models/image/best_sign.pt') 

    # OCR engine for speed-limit signs
    speed_limit_ocr = SpeedLimitOCR(['en'])

    l_conf_threshold=0.5 
    b_conf_threshold=0.5
    s_conf_threshold=0.4
    speed_limit_ocr_conf_threshold = 80
    diff_conf = 0.1

    # Start video stream
    print("===========================Starting video capture...")
    cap = cv2.VideoCapture(0)
    count = 0
    PROCESS_EVERY_N = 10

    while cap.isOpened():
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        
        count += 1
        if (count % PROCESS_EVERY_N== 0):        
            # Each iteration, reset current_traffic_control_flag
            current_traffic_control_flag = traffic_control_flag.copy()

            # ===================================
            # 1: Traffic-light Detection via YOLO
            # =================================== 
            # Detect traffic lights
            l_results = l_model(frame, verbose=False)                 

            # For each traffic light
            for l_box in l_results[0].boxes:
                if l_box.conf[0] > l_conf_threshold:

                    # Crop around the detected traffic light
                    l_x, l_y, l_w, l_h = map(int, l_box.xywh[0])  
                    cropped_traffic_light_frame = crop_image(frame, (l_x - l_w/2, l_y - l_h/2, l_w, l_h))                 
                    
                    # Detect bulbs inside the light
                    b_results = b_model(cropped_traffic_light_frame, verbose=False)
                    b_class_names = b_model.names    
                    
                    # Determine the dominant color for straight, turn-left, and turn-right directions
                    dominant_color, dominant_color_box_list = analyze_light_bulbs(
                        b_results, b_class_names, b_conf_threshold, diff_conf
                    )              

                    if dominant_color.get("forward") == "red":
                        current_traffic_control_flag["RedTrafficLight"] = True
                    if dominant_color.get("left") == "red":
                        current_traffic_control_flag["RedLeftTurnTrafficLight"] = True
                    if dominant_color.get("right") == "red":
                        current_traffic_control_flag["RedRightTurnTrafficLight"] = True

            # =========================================
            # 2: Traffic-sign Detection via YOLO + OCR
            # =========================================                    
            # Detect traffic signs.
            s_results = s_model(frame, verbose=False)          
            s_class_names = s_model.names 

            # Iterate through all detected traffic signs.           
            best_speed_limit_conf = 0
            best_speed_limit_value = None
            for s_box in s_results[0].boxes:
                if s_box.conf[0] > s_conf_threshold:                         
                    s_box_name = s_class_names[int(s_box.cls[0].item())]
                    match s_box_name:
                        case "stop":
                            current_traffic_control_flag["StopTrafficSign"]=True                                                 
                        case "stopAhead":
                            current_traffic_control_flag["StopAheadTrafficSign"]=True
                        case "yield":
                            current_traffic_control_flag["YieldTrafficSign"]=True
                        case "yieldAhead":
                            current_traffic_control_flag["YieldAheadTrafficSign"]=True
                        case _:
                            # Treat as potential speed-limit sign
                            s_x1, s_y1, s_x2, s_y2 = map(int, s_box.xyxy[0])                                                       
                            cropped = frame[s_y1:s_y2, s_x1:s_x2]
                            speed_limit_value = speed_limit_ocr.extract_speed_limit(cropped, speed_limit_ocr_conf_threshold) 
                            if speed_limit_value is not None:                                                                    
                                current_traffic_control_flag["SpeedLimitTrafficSign"]=True   
                                if (s_box_conf := s_box.conf[0].item()) >= best_speed_limit_conf:
                                    best_speed_limit_conf, best_speed_limit_value = s_box_conf, speed_limit_value                   

            # =============================================================
            # 3: Add the detection status of current frame to history queue
            # ============================================================= 
            traffic_control_flag_history.append(current_traffic_control_flag) 
                   
            # =================
            # 4: Voice Playback
            # =================   
            # Voice Alert for turn-signal coaching
            if not turn_signal_detection_manager.is_blinker_on() and imu_controller.detect_turn() != "Straight":
                voice_playback_manager.speak_queued("Do not forget to use your turn signal when turning! ")

            # Voice Alert for speeding coaching
            if current_traffic_control_flag["SpeedLimitTrafficSign"] and not last_confirmed_traffic_control_flag["SpeedLimitTrafficSign"]:
                gps_controller.update()
                driving_mph = gps_controller.get_speed_mph()
                if best_speed_limit_value is not None and driving_mph > best_speed_limit_value:                      
                    voice_playback_manager.speak_queued("You are above the detected speed limit. ")   
                last_confirmed_traffic_control_flag["SpeedLimitTrafficSign"] = current_traffic_control_flag["SpeedLimitTrafficSign"]
                
            # Voice Alert for traffic-control coaching with 3-frame confirmation
            for key in current_traffic_control_flag:
                # If the traffic-control is detected in three consecutive frames and was not previously confirmed as detected                   
                if all(traffic_control_flag_history[i][key] for i in range(3)) and not last_confirmed_traffic_control_flag[key]:
                    if key in ("RedTrafficLight", "RedLeftTurnTrafficLight", "RedRightTurnTrafficLight", "StopTrafficSign", "StopAheadTrafficSign", "YieldTrafficSign", "YieldAheadTrafficSign"):
                        voice_playback_manager.speak_queued(f"{key} detected. ")               

                    last_confirmed_traffic_control_flag[key] = current_traffic_control_flag[key]
                                     
                # If the traffic-control is not detected in three consecutive frames and was previously confirmed as detected  
                if all(not traffic_control_flag_history[i][key] for i in range(3)) and last_confirmed_traffic_control_flag[key]:              
                    if key in ("RedTrafficLight", "RedLeftTurnTrafficLight", "RedRightTurnTrafficLight"):
                        voice_playback_manager.speak_queued(f"{key} no longer detected.")
                          
                    last_confirmed_traffic_control_flag[key] = current_traffic_control_flag[key]

    
            # =======
            # 5: Exit
            # =======
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if (count % PROCESS_EVERY_N == 0):
               # Small delay to ease CPU load
               sleep(0.20) 

    cap.release()
    cv2.destroyAllWindows()

    turn_signal_detection_manager.stop()
    voice_playback_manager.stop()

if __name__ == "__main__":
    main()
            
