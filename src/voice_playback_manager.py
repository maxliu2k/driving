import io
import sys
import wave
import subprocess
from piper import PiperVoice
import threading
import queue
#from playsound import playsound

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
        # aplay can also read from stdin if you pass "-" as filename:
        subprocess.run(["aplay", "-"], input=buf.read(), check=True)

    def speak(self, text: str):
        self.speak_to_file(text)


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
            # self.voice_engine.speak(text)
            # playsound(text) 
            print(text)
            self.voice_queue.task_done()

    # Start the voice worker thread.
    def start(self):
        self.worker_thread.start()

    # Stop the voice worker thread and clean up resources.
    def stop(self):
        self.voice_queue.put(None)
        self.worker_thread.join()


def main():
    # Path to your Piper TTS model
    model_path = "path/to/voice_model.onnx"

    # Initialize the voice playback manager
    voice_manager = VoicePlaybackManager(model_path)

    try:
        # Queue up some text messages to be spoken
        voice_manager.speak_queued("Hello, this is a test.")
        voice_manager.speak_queued("Turn left at the next intersection.")
        voice_manager.speak_queued("Drive safely!")

        # Keep the main thread alive while background thread processes
        import time
        time.sleep(5)  # Adjust depending on how long you expect playback to take

    except KeyboardInterrupt:
        print("\nStopping voice playback...")
    finally:
        # Ensure the voice worker thread stops cleanly
        voice_manager.stop()
        print("Voice playback stopped.")


if __name__ == "__main__":
    main()