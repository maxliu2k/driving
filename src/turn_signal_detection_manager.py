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

# ===============================
# Turn Signal Detection Engine:Core engine for turn signal detection using a Mel-Spectrogram CNN model.
#                              Responsible for model loading, audio processing, and inference.#
# ===============================
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

        #print(f"\n===========================🎙️ Mic @ {self.sr} Hz | class='{self.pos_name}' threshold={threshold}. Ctrl+C to stop.")

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
            #print(f"===========================p({self.pos_name})={p:.2f}", end="\r")
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
        #print(f"===========================Turn Signal Probability: {prob:.4f} at {timestamp:.2f}")

    # Callback when the turn signal deactivates.
    def _on_deactivate(self, timestamp: float):
        self.blinker_on = False
        #print(f"===========================Turn Signal Deactivated at {timestamp:.2f}")

    # Start the detection engine with callbacks.  
    def start(self):
        self.engine.start_detection(
            on_detect=self._on_detect,
            on_deactivate=self._on_deactivate
        )

    # Stop the detection engine.
    def stop(self):
        self.engine.stop_detection()






def main():
    # Initialize the detection manager with your trained model
    manager = TurnSignalDetectionManager("models/sound/turn_signal_cnn.pt", "cpu")

    try:
        print("Starting turn signal detection...")
        manager.start()   # This calls engine.start_detection() internally

        # Keep program running to allow microphone stream to work
        while True:
            time.sleep(1)
            # You can check blinker status
            if manager.is_blinker_on():
                print("=========================== Blinker is ON")
            else:
                print("=========================== Blinker is OFF")

    except KeyboardInterrupt:
        print("\nStopping turn signal detection...")
    finally:
        manager.stop()
        print("Turn signal detection stopped.")

if __name__ == "__main__":
    main()