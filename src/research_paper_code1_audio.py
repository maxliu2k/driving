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


# ===============================
# Audio Model
# ===============================

import torch
import torchaudio
from torch.utils.data import Dataset, DataLoader
import os
import json


# Create CNN architecture
class SmallAudioCNN(torch.nn.Module):
    def __init__(self, n_mels: int, n_classes: int):
        super().__init__()
        self.features = torch.nn.Sequential(
            torch.nn.Conv2d(1, 32, 3, padding=1), torch.nn.BatchNorm2d(32), torch.nn.ReLU(),
            torch.nn.Conv2d(32, 32, 3, padding=1), torch.nn.BatchNorm2d(32), torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),

            torch.nn.Conv2d(32, 64, 3, padding=1), torch.nn.BatchNorm2d(64), torch.nn.ReLU(),
            torch.nn.Conv2d(64, 64, 3, padding=1), torch.nn.BatchNorm2d(64), torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),

            torch.nn.Conv2d(64, 128, 3, padding=1), torch.nn.BatchNorm2d(128), torch.nn.ReLU(),
            torch.nn.Conv2d(128, 128, 3, padding=1), torch.nn.BatchNorm2d(128), torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(128, 64), torch.nn.ReLU(), torch.nn.Dropout(0.2),
            torch.nn.Linear(64, n_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))


# Create Dataset Class
class TurnSignalSoundDataset(Dataset):
    def __init__(self, root_dir, cfg, labels):
        self.root_dir = root_dir
        self.labels = labels
        self.cfg = cfg  # Store cfg for use in __getitem__
        self.filepaths = []

        for label in labels:
            label_path = os.path.join(root_dir, label)
            for fname in os.listdir(label_path):
                if fname.endswith(".wav"):
                    self.filepaths.append((os.path.join(label_path, fname), label))

        self.label_to_idx = {label: idx for idx, label in enumerate(labels)}

        self.melspec = torchaudio.transforms.MelSpectrogram(
            sample_rate=cfg["sample_rate"],
            n_fft=cfg["n_fft"],
            hop_length=cfg["hop_length"],
            n_mels=cfg["n_mels"]
        )
        self.amp2db = torchaudio.transforms.AmplitudeToDB(stype="power")

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        filepath, label = self.filepaths[idx]
        waveform, sr = torchaudio.load(filepath)

        if sr != self.cfg["sample_rate"]:
            waveform = torchaudio.functional.resample(waveform, sr, self.cfg["sample_rate"])

        mel = self.melspec(waveform)
        mel_db = self.amp2db(mel)

        # Add channel dimension for CNN (C=1)
        if mel_db.ndim == 2:
            mel_db = mel_db.unsqueeze(0)

        return mel_db, self.label_to_idx[label]


def main():
    # Define Configuration
    cfg = {
        "sample_rate": 16000,
        "n_fft": 1024,
        "hop_length": 512,
        "n_mels": 64,
        "batch_size": 8,
        "epochs": 20,
        "learning_rate": 1e-3,
        "f_min": 20.0,
        "f_max": 8000.0,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
    }

    labels = ["noise", "turn"]

    # Create datasets and loaders
    train_dataset = TurnSignalSoundDataset("data/train", cfg, labels)
    val_dataset = TurnSignalSoundDataset("data/val", cfg, labels)

    train_loader = DataLoader(train_dataset, batch_size=cfg["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=cfg["batch_size"])

    # Initialize model
    n_classes = len(labels)
    model = SmallAudioCNN(cfg["n_mels"], n_classes).to(cfg["device"])

    # Loss and optimizer
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["learning_rate"])

    # Train and validate
    for epoch in range(cfg["epochs"]):
        # Training
        model.train()
        total_loss, total_correct = 0, 0

        for mel, label in train_loader:
            mel, label = mel.to(cfg["device"]), label.to(cfg["device"])

            optimizer.zero_grad()
            output = model(mel)
            loss = criterion(output, label)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            total_correct += (output.argmax(1) == label).sum().item()

        train_acc = total_correct / len(train_loader.dataset)
        print(f"Epoch {epoch+1}/{cfg['epochs']} Train Loss: {total_loss:.3f} Train Acc: {train_acc:.3f}")

        # Validation
        model.eval()
        val_correct, val_loss = 0, 0
        with torch.no_grad():
            for mel, label in val_loader:
                mel, label = mel.to(cfg["device"]), label.to(cfg["device"])
                output = model(mel)
                loss = criterion(output, label)

                val_loss += loss.item()
                val_correct += (output.argmax(1) == label).sum().item()

        val_acc = val_correct / len(val_loader.dataset)

    # Save model to specified path
    os.makedirs("models/sound", exist_ok=True)
    torch.save({
        "model": model.state_dict(),
        "labels": labels,
        "cfg": cfg
    }, os.path.join("models", "sound", "turn_signal_cnn.pt"))

if __name__ == "__main__":
    main()
