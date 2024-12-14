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

import wave
from piper import Piper
import subprocess

class Voice:
    def __init__(self, model_path, config_path):
        self.piper = Piper(model_path, config_path)

    def speak(self, text):
        try:
            audio = self.piper.synthesize(text)

            with wave.open("temp.wav", "wb") as f:
                f.setnchannels(1) # mono
                f.setsampwidth(2) # 16 bits
                f.setframerate(self.piper.sample_rate)
                f.writeframes(audio)

            subprocess.run(["aplay", "temp.wav"], check=True)
        except Exception as e:
            print(f"Error: {e}")