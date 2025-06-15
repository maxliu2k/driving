# Test the functionality of the microphone

import pyaudio
import numpy as np
import time

# Set the parameters for the audio
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1  # Mono audio
SAMPLE_RATE = 44100  # 44.1kHz sample rate
CHUNK = 1024  # Number of frames per buffer

blinker_on = false

def list_microphones():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"Device {i}: {device_info['name']}")
    p.terminate()

def detect_turn_signal_click(audio_data, rate):
    """
    Detect if the provided audio data contains a short transient click
    typical of a turn signal click.

    Methodology:
    1. 
    """
    global blinker_on

    p = pyaudio.PyAudio()

    # stream = p.open(format=FORMAT,

    while True:
        # read the audio data

        # compute RMS

        # update flag if RMS exceeds threshold

        # small delay to avoid excessive CPU usage
        time.sleep(0.1)

    pass

if __name__ == "__main__":
    print("Available Microphones:")
    list_microphones()