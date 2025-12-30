"""
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


class SpeedLimitOCR:
    # Initialize EasyOCR reader with the given language list.
    def __init__(self, language_list):
        self.reader = easyocr.Reader(language_list)

    # Detect and extract the speed limit number.
    def extract_speed_limit(self, frame, conf_threshold):
        speed_limit_value = None
        target_words = ['speed', 'limit']
        found_targets = {target: False for target in target_words}

        # OCR detection
        results = self.reader.readtext(frame)
        all_lowercase_text = ' '.join([text for (_, text, _) in results]).lower()

        # Check if "speed" and "limit" appear in OCR text
        for _, text, _ in results:
            for target in target_words:
                if not found_targets[target] and fuzz.ratio(text.lower(), target) > conf_threshold:
                    found_targets[target] = True

        # Extract numeric value if both words are found
        speed_limit_value = 1000
        if found_targets['speed'] and found_targets['limit']:
            match = re.search(r'\b\d{2}\b', all_lowercase_text)
            if match:
                speed_limit_value = int(match.group())

        return speed_limit_value
    

# ========================================
# Main function
# ========================================
def main():


    #
   
    print("Starting turn signal detection engine...")
    turn_signal_detection_manager = TurnSignalDetectionManager("models/sound/turn_signal_cnn.pt", "cpu")
    turn_signal_detection_manager.start()

    l_conf_threshold=0.5 
    b_conf_threshold=0.5
    s_conf_threshold=0.4
    speed_limit_ocr_conf_threshold = 0.8

    # Load YOLO model
    l_model = YOLO('models/image/best_light.pt')
    b_model = YOLO('models/image/best_bulb.pt')
    s_model = YOLO('models/image/best_sign.pt')
    
    speed_limit_ocr = SpeedLimitOCR(['en'])

    # Start video stream
    print("Starting video capture...")
    cap = cv2.VideoCapture(0)
    count = 0
    PROCESS_EVERY_N = 10
    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        
        if (count % PROCESS_EVERY_N== 0):       


            # 

            # =======================================
            # 1: Traffic Signs and Traffic Lights Detection via YOLO
            # =======================================
            # Detect traffic signs.
            s_results = s_model(frame, verbose=False)          
            s_class_names = s_model.names
            for s_box in s_results[0].boxes:
                if s_box.conf[0] > s_conf_threshold:  
                    s_box_name = s_class_names[int(s_box.cls[0].item())]                                        
                    if "speedlimit" in s_box_name.lower(): 
                        s_x1, s_y1, s_x2, s_y2 = map(int, s_box.xyxy[0])                                                      
                        cropped = frame[s_y1:s_y2, s_x1:s_x2]
                        speed_limit_value = speed_limit_ocr.extract_speed_limit(cropped, speed_limit_ocr_conf_threshold)
                            

            # Detect traffic lights
            l_results = l_model(frame, verbose=False)   
            l_class_names = l_model.names            

            # For each traffic light
            for l_box in l_results[0].boxes:
                if l_box.conf[0] > l_conf_threshold:
                    # Crop traffic light box
                    l_x, l_y, l_w, l_h = map(int, l_box.xywh[0])  
                    cropped_traffic_light_frame = crop_image(frame, (l_x - l_w/2, l_y - l_h/2, l_w, l_h))                     

                    # Detect light bulbs in the cropped image.
                    b_results = b_model(cropped_traffic_light_frame, verbose=False)
                    b_class_names = b_model.names              


            b_conf_threshold
            s_conf_threshold
            l_class_names
            b_results
            b_class_names
            s_results
            s_class_names
"""


import os
import shutil
from ultralytics import YOLO

# ===============================
# Image Model
# ===============================
# Train a YOLOv8 model with given dataset and parameters.
def train_yolo_model(best_model_save_to_path, 
                     yaml_path, project, 
                     epochs=100, batch=32, imgsz=640, 
                     save_period=10, patience=20, close_mosaic=10, 
                     cos_lr=True, device=0, workers=2, cache=True, seed=0,
                     hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, 
                     degrees=0.0, translate=0.1, scale=0.5, shear=0.0, perspective=0.0,
                     flipud=0.0, fliplr=0.5, 
                     bgr=0.0, mosaic=1.0, mixup=0.0, cutmix=0.0):
     
    # Load a pretrained YOLOv8 model
    model = YOLO("yolov8n.pt")

    # Train the model
    model.train(data=yaml_path, project=project, 
                epochs=epochs, batch=batch, imgsz=imgsz,
                save_period=save_period, patience=patience, close_mosaic=close_mosaic, 
                cos_lr=cos_lr, device=device, workers=workers, cache=cache, seed=seed,
                hsv_h=hsv_h, hsv_s=hsv_s, hsv_v=hsv_v,
                degrees=degrees, translate=translate, scale=scale, shear=shear, perspective=perspective,
                flipud=flipud, fliplr=fliplr,
                bgr=bgr, mosaic=mosaic, mixup=mixup, cutmix=cutmix)

    # Copy best.pt to specified path
    best_model_path = os.path.join(os.path.join(project, os.listdir(project)[-1]), "weights", "best.pt")
    os.makedirs(os.path.dirname(best_model_save_to_path), exist_ok=True)
    shutil.copy(best_model_path, best_model_save_to_path)


def main():
    # Train traffic light model
    l_yaml = "dataset/traffic_light/data.yaml"
    l_results = "results/traffic_light"
    l_best_model_save_to_path = "models/image/best_light.pt"
    train_yolo_model(best_model_save_to_path=l_best_model_save_to_path, 
                    data_yaml=l_yaml, project=l_results,
                    hsv_h=0.0, hsv_s=0.4, hsv_v=0.4, 
                    degrees=5, scale=0.3,
                    fliplr=0.2,
                    mosaic=0.5)
    
    # Train traffic bulb model
    b_yaml = "dataset/traffic_bulbs/data.yaml"
    b_results = "results/traffic_bulbs"
    b_best_model_save_to_path = "models/image/best_bulb.pt"
    train_yolo_model(data_yaml=b_yaml, project=b_results, best_model_save_to_path=b_best_model_save_to_path)
    
    # Train traffic sign model
    s_yaml = "dataset/traffic_signs/data.yaml"
    s_results = "results/traffic_signs"
    s_best_model_save_to_path = "models/image/best_sign.pt"
    train_yolo_model(best_model_save_to_path=s_best_model_save_to_path, 
                    data_yaml=s_yaml, project=s_results,
                    hsv_h=0.0, hsv_s=0.2, hsv_v=0.2, 
                    degrees=5, scale=0.3,
                    fliplr=0.0,
                    mosaic=0.2)
    

if __name__ == "__main__":
    main()
