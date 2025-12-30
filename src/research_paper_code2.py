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

import argparse, time, os
from pathlib import Path
from typing import Tuple, List, Optional, Callable
import numpy
import torchaudio #pip install torchaudio==2.4.1
import sounddevice
from utils import *
from small_audio_cnn import SmallAudioCNN

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

    
# ================================================
# IMU Controller: Controls the IMU(MPU6050) module
# ================================================
class IMUController:

    # MPU6050 Registers
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

    # Offsets for calibration
    Ax_offset = 0.05
    Ay_offset = -0.01
    Az_offset = -1.11
    Gx_offset = 0.29
    Gy_offset = 0.07
    Gz_offset = 0.09

    # Filtering and Thresholds
    GYRO_WINDOW = 10
    GYRO_THRESHOLD = 5.0  # degrees/sec

    # Initializes the I2C bus, sets device address, creates a gyro buffer, and initializes the MPU6050 sensor.
    def __init__(self, bus_id=1, device_address=0x68):
        self.bus = smbus.SMBus(bus_id)
        self.device_address = device_address
        self.gyro_buffer = deque(maxlen=self.GYRO_WINDOW)
        self.MPU_Init()

    # Configures MPU6050 registers.
    def MPU_Init(self):
        self.bus.write_byte_data(self.device_address, self.SMPLRT_DIV, 7)
        self.bus.write_byte_data(self.device_address, self.PWR_MGMT_1, 1)
        self.bus.write_byte_data(self.device_address, self.CONFIG, 0)
        self.bus.write_byte_data(self.device_address, self.GYRO_CONFIG, 24)
        self.bus.write_byte_data(self.device_address, self.INT_ENABLE, 1)

    # Read 16-bit raw data from a sensor register.
    def read_raw_data(self, addr):
        high = self.bus.read_byte_data(self.device_address, addr)
        low = self.bus.read_byte_data(self.device_address, addr + 1)
        value = (high << 8) | low
        if value > 32768:
            value -= 65536
        return value

    # Return calibrated accelerometer and gyroscope values.
    def get_motion_data(self):
        acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
        acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
        acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)
        gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
        gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)

        Ax = acc_x / 16384.0 + self.Ax_offset
        Ay = acc_y / 16384.0 + self.Ay_offset
        Az = acc_z / 16384.0 + self.Az_offset
        Gx = gyro_x / 131.0 + self.Gx_offset
        Gy = gyro_y / 131.0 + self.Gy_offset
        Gz = gyro_z / 131.0 + self.Gz_offset

        return Ax, Ay, Az, Gx, Gy, Gz

    # Detect left or right turn based on gyro readings.
    def detect_turn(self):
        _, _, _, Gx, Gy, Gz = self.get_motion_data()
        self.gyro_buffer.append(Gy)

        gyro_avg = sum(self.gyro_buffer) / len(self.gyro_buffer)

        if abs(gyro_avg) > self.GYRO_THRESHOLD:
            return "Right Turn" if gyro_avg > 0 else "Left Turn"
        return "Straight"
    

# ==========================================================================================
# GPS Controller: Control the GPS module - handles initialization, location, and speed data.
# ==========================================================================================
class GPSController:
    # Initializes the GPS connection, configures output sentences, and sets the update rate.
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, timeout=30, update_rate=1.0):
        # Initialize UART connection
        self.uart = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)

        # Configure GPS to output only RMC (Recommended Minimum) and GGA (Fix Data)
        self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

        # Set update frequency in milliseconds
        self.gps.send_command(f'PMTK220,{int(1000/update_rate)}'.encode())

        # Output interval in seconds
        self.update_rate = update_rate  

    # Fetch new data from the GPS module.
    def update(self):
        self.gps.update()

    # Return True if GPS has a valid fix, False otherwise.
    def has_fix(self):   
        return self.gps.has_fix

    # Return (latitude, longitude) if available, else None.
    def get_location(self):       
        if not self.gps.has_fix:
            return None
        return (self.gps.latitude, self.gps.longitude)

    # Return speed in mph if available, else None.
    def get_speed_mph(self):  
        if not self.gps.has_fix:   
            print('===========================GPS Waiting for fix...')
            return None
        else:
            if self.gps.speed_knots is not None:           
                return self.gps.speed_knots * 1.15078
            else:
                print('===========================Driving speed is not available')
                return None
            

# =============================================================
# TTS Voice Engine: Core text-to-speech engine using PiperVoice
# =============================================================
class TTSVoiceEngine:
    # Initialize TTS engine with model path.
    def __init__(self, model_path: str):
        self.voice = PiperVoice.load(model_path, use_cuda=False)

    # Convert text to speech, save as WAV, and play it.
    def speak_to_file(self, text: str, filename: str = "misc/temp.wav"):
        with wave.open(filename, "wb") as wav_file:
            self.voice.synthesize(text, wav_file)
        player = "afplay" if sys.platform == "darwin" else "aplay"
        subprocess.run(["aplay", filename], check=True)

    # Convert text to speech and play directly from memory.
    def speak_raw(self, text: str):
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_buf:
            self.voice.synthesize(text, wav_buf)
        buf.seek(0)
        player = "afplay" if sys.platform == "darwin" else "aplay"
        subprocess.run(["aplay", "-"], input=buf.read(), check=True)

    def speak(self, text: str):
        self.speak_raw(text)

# ==========================================================================================
# Voice Playback Manager: Manages TTSVoiceEngine and queued playback in a background thread.
# ==========================================================================================
class VoicePlaybackManager:
    # Initialize voice playback manager with a TTS engine and worker thread.
    def __init__(self, model_path: str):
        self.voice_queue = queue.Queue()
        self.voice_engine = TTSVoiceEngine(model_path)
        self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)    

    # Add text to the voice queue for playback.
    def speak_queued(self, text: str):
        self.voice_queue.put(text)

    # Continuously process queued text and play speech.
    def _voice_worker(self):
        while True:
            text = self.voice_queue.get()
            if text is None:
                break
            self.voice_engine.speak(text)
            self.voice_queue.task_done()

    # Start the voice worker thread.
    def start(self):
        self.worker_thread.start()

    # Stop the voice worker thread and clean up resources.
    def stop(self):
        self.voice_queue.put(None)
        self.worker_thread.join()


# =====================================================================================================
# Turn Signal Detection Engine:Core engine for turn signal detection using a Mel-Spectrogram CNN model.
# =====================================================================================================
class TurnSignalDetectionEngine:
    # Initialize the detection engine with model path and device.
    def __init__(self, model_path: str, device: str):
        self.model_path = model_path
        self.labels = None
        self.cfg = None
        self.device = str
        self.model = None
        self.melspec = None
        self.amp2db = None

        self.label_to_idx = {}
        self.pos_name = ""
        self.pos_idx = 0
        self.sr = 16000
        self.W = 0
        self.S = 0
        self.ring = None
        self.last_fire = 0.0
        self.silence = None
        self.stream = None

    # Load the CNN audio model.
    def load_model(self):   
        ckpt = torch.load(self.model_path, map_location="cpu")
        self.labels = ckpt["labels"]
        self.cfg = ckpt["cfg"]

        self.device = resolve_device(self.device or self.cfg.get("device", "cpu"))
        self.model = SmallAudioCNN(self.cfg["n_mels"], len(self.labels))
        self.model.load_state_dict(ckpt["model"], strict=True)
        self.model.eval().to(self.device)

        # mel/db params must match training
        f_min = self.cfg.get("f_min", 20.0)
        f_max = self.cfg.get("f_max", self.cfg["sample_rate"] // 2)
        self.melspec = torchaudio.transforms.MelSpectrogram(
            sample_rate=self.cfg["sample_rate"],
            n_fft=self.cfg["n_fft"],
            hop_length=self.cfg["hop_length"],
            n_mels=self.cfg["n_mels"],
            power=2.0,
            center=True,
            f_min=f_min,
            f_max=f_max,
        )
        self.amp2db = torchaudio.transforms.AmplitudeToDB(stype="power")
        
    # Generate probability for the positive class.
    @torch.no_grad()
    def probs_from_waveform(self, x_1xT: torch.Tensor) -> numpy.ndarray:
        
        mel = self.melspec(x_1xT)
        mel = self.amp2db(mel)
        mel = (mel - mel.mean()) / (mel.std() + 1e-6)
        logits = self.model(mel.unsqueeze(0).to(self.device)).squeeze(0)
        return torch.softmax(logits, dim=-1).cpu().numpy()
    
    # Start microphone detection stream.
    def start_detection(self, positive_class=None, 
                        window_s: float = 1.5, step_s: float = 0.25, 
                        threshold: float = 0.45, min_gap_s: float = 1.0,
                        on_detect: Optional[Callable] = None,
                        on_deactivate: Optional[Callable] = None):
        
        self.load_model()
        self.label_to_idx = {n: i for i, n in enumerate(self.labels)}
        self.pos_name = positive_class or ("turn" if "turn" in self.label_to_idx else self.labels[0])
        self.pos_idx = self.label_to_idx[self.pos_name]

        self.sr = self.cfg["sample_rate"]
        self.W = int(window_s * self.sr)
        self.S = int(step_s * self.sr)

        self.ring = torch.zeros(self.W, dtype=torch.float32)
        self.last_fire = 0.0
        self.silence = [] # call on_deactivate after not getting a hit 5 times in a row

        def callback(indata, frames, time_info, status):
            if status:
                pass
            x = torch.from_numpy(indata.copy()).float()
            if x.ndim == 2:
                x = x.mean(dim=1)
            if x.numel() < self.S:
                return
            self.ring = torch.roll(self.ring, -self.S)
            self.ring[-self.S:] = x[:self.S]

            p = self.probs_from_waveform(self.ring.unsqueeze(0))[self.pos_idx]

            now = time.time()
            if p >= threshold and (now - self.last_fire) >= min_gap_s:
                self.last_fire = now
                print(f"===========================🔔 Detected {self.pos_name} (p={p:.2f}) at {time.strftime('%H:%M:%S')}")
                self.silence = []
                if on_detect:
                    on_detect(p, now)
            else:
                self.silence.append(p)
                if len(self.silence) > 5:
                    self.silence = []
                    if on_deactivate:
                        on_deactivate(now)

        try:
            self.stream = sounddevice.InputStream(
                samplerate=self.sr,
                channels=1,
                blocksize=self.S,
                callback=callback
            )
            self.stream.start()
        except Exception as e:
            print(f"===========================Microphone Error: {e}")

    # Stop microphone detection stream.
    def stop_detection(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

# ===============================
# Turn Signal Detection Manager:Manages TurnSignalDetectionEngine and detection state.
# ===============================
class TurnSignalDetectionManager:
    # Initialize manager with detection engine and blinker state.
    def __init__(self, model_path: str, device: str):
        self.engine = TurnSignalDetectionEngine(model_path, device)
        self.blinker_on = False

    # Check if the blinker is currently on.
    def is_blinker_on(self) -> bool:
        return self.blinker_on 

    # Callback when a turn signal is detected.
    def _on_detect(self, prob: float, timestamp: float):
        self.blinker_on = True

    # Callback when the turn signal deactivates.
    def _on_deactivate(self, timestamp: float):
        self.blinker_on = False

    # Start the detection engine with callbacks.  
    def start(self):
        self.engine.start_detection(
            on_detect=self._on_detect,
            on_deactivate=self._on_deactivate
        )

    # Stop the detection engine.
    def stop(self):
        self.engine.stop_detection()
