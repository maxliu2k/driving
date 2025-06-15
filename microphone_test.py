import threading
import audioop
import pyaudio
import time

# Set the parameters for the audio
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1  # Mono audio
SAMPLE_RATE = 44100  # 44.1kHz sample rate
CHUNK = 1024  # Number of frames per buffer

blinker_on = False

def list_microphones():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"Device {i}: {device_info['name']}")
    p.terminate()

def detect_turn_signal_click(threshold=500, chunk=1024, rate=44100, device_index=None):
    """
    Detect if the provided audio data contains a short transient click
    typical of a turn signal click.

    Methodology:
    1. 
    """
    global blinker_on
    current_blinker_state = False

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
        channels=1,
        rate=rate,
        input=True,
        frames_per_buffer=chunk,
        input_device_index=device_index)

    while True:
        data = stream.read(chunk, exception_on_overflow=False)
        # Compute RMS; audioop.rms returns RMS of signed 16-bit samples :contentReference[oaicite:4]{index=4}
        rms = audioop.rms(data, 2)
        # Update flag if RMS exceeds threshold
        blinker_on = rms > threshold
        if blinker_on != current_blinker_state:
            current_blinker_state = blinker_on
            if blinker_on:
                print("Turn signal detected: Blinker ON")
            else:
                print("Turn signal detected: Blinker OFF")
        # small delay to avoid excessive CPU usage
        time.sleep(0.1)

if __name__ == "__main__":
    print("Available Microphones:")
    list_microphones()