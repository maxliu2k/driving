# import pyttsx3
# import subprocess

# class Voice:
#     """
#     sapi5: Microsoft Speech API
#     espeak: Linux
#     nsss: Mac OS
#     """
#     def __init__(self):
#         self.engine = pyttsx3.init("sapi5")
#         voice = self.engine.getProperty("voices")
#         self.engine.setProperty("voice", voice[0].id)

#     def speak(self, text):
#         try:
#             self.engine.say(text)
#             self.engine.runAndWait()

#             # Create the wav file
#             # subprocess.run(["pico2wave", "-w", "temp.wav", text], check=True)

#             # Play the wav file
#             # subprocess.run(["aplay", "temp.wav"], check=True)
#         except Exception as e:
#             print(f"===========================Voice Engine Error: {e}")

import io
import sys
import wave
import subprocess
from piper import PiperVoice

class Voice:
    def __init__(self, model_path: str):
        # Load your ONNX model + JSON config (auto‑finds model.json next to .onnx)
        # On Pi, we'll force CPU inference:
        self.voice = PiperVoice.load(model_path, use_cuda=False)

    def speak_to_file(self, text: str, filename: str = "misc/temp.wav"):
        # 1) Write out a standard 16‑bit mono WAV:
        with wave.open(filename, "wb") as wav_file:
            self.voice.synthesize(text, wav_file)
        # 2) Play it back via ALSA’s aplay:
        player = "afplay" if sys.platform == "darwin" else "aplay"
        subprocess.run([player, filename], check=True)

    def speak_raw(self, text: str):
        # If you prefer in‑memory playback:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_buf:
            self.voice.synthesize(text, wav_buf)
        buf.seek(0)
        # aplay can also read from stdin if you pass "-" as filename:
        subprocess.run(["aplay", "-"], input=buf.read(), check=True)
    
    def speak(self, text: str):
        """Default speak() calls file-based playback."""
        self.speak_to_file(text)

if __name__ == "__main__":
    v = Voice("models/voice/piper.onnx")
    v.speak_to_file("Hello from your Raspberry Pi!", "mobile_app/max_driving/assets/audios/test.wav")

    v.speak_to_file("red light detected. please slow down.", "mobile_app/max_driving/assets/audios/red_light_slow.wav")
    v.speak_to_file("red light no longer detected", "mobile_app/max_driving/assets/audios/red_light_off.wav")

    v.speak_to_file("red left light detected", "mobile_app/max_driving/assets/audios/red_left_light.wav")
    v.speak_to_file("red left light no longer detected", "mobile_app/max_driving/assets/audios/red_left_light_off.wav")

    v.speak_to_file("stop sign detected", "mobile_app/max_driving/assets/audios/stop.wav")
    v.speak_to_file("stop ahead sign detected", "mobile_app/max_driving/assets/audios/stop_ahead.wav")
    v.speak_to_file("yield sign detected", "mobile_app/max_driving/assets/audios/yield.wav")
    v.speak_to_file("yield ahead sign detected", "mobile_app/max_driving/assets/audios/yield_ahead.wav")

    v.speak_to_file("Do not forget to use your turn signal when turning!", "mobile_app/max_driving/assets/audios/turn_signal.wav")
    v.speak_to_file("You are above the detected speed limit of 45. Your speed is 48.", "mobile_app/max_driving/assets/audios/speed_limit.wav")
    # or
    # v.speak_raw("Streaming from memory!")