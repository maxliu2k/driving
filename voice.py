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
#             print(f"Error: {e}")

import io
import wave
import subprocess
from piper import PiperVoice

class Voice:
    def __init__(self, model_path: str):
        # Load your ONNX model + JSON config (auto‑finds model.json next to .onnx)
        # On Pi, we'll force CPU inference:
        self.voice = PiperVoice.load(model_path, use_cuda=False)

    def speak_to_file(self, text: str, filename: str = "temp.wav"):
        # 1) Write out a standard 16‑bit mono WAV:
        with wave.open(filename, "wb") as wav_file:
            self.voice.synthesize(text, wav_file)
        # 2) Play it back via ALSA’s aplay:
        subprocess.run(["aplay", filename], check=True)

    def speak_raw(self, text: str):
        # If you prefer in‑memory playback:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_buf:
            self.voice.synthesize(text, wav_buf)
        buf.seek(0)
        # aplay can also read from stdin if you pass "-" as filename:
        subprocess.run(["aplay", "-"], input=buf.read(), check=True)

if __name__ == "__main__":
    v = Voice("en_US-lessac-medium.onnx")
    v.speak_to_file("Hello from your Raspberry Pi!")
    # or
    # v.speak_raw("Streaming from memory!")
