import argparse, time, os
from pathlib import Path
from typing import Tuple, List, Optional

import numpy as np
import torch
import torch.nn as nn
import torchaudio

# Optional decoders for files
try:
    import soundfile as sf
    _HAVE_SF = True
except Exception:
    _HAVE_SF = False

try:
    from pydub import AudioSegment
    _HAVE_PYDUB = True
except Exception:
    _HAVE_PYDUB = False


# -----------------------------
# Model
# -----------------------------
class SmallAudioCNN(nn.Module):
    def __init__(self, n_mels: int, n_classes: int):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.Conv2d(128, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, n_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))



class TurnSignalDetector:
    def __init__(self):
        self.model = None
        self.melspec = None
        self.amp2db = None
        self.dev = None
        self.cfg = None
        self.labels = None
        self.stream = None

        # mic state
        self.label_to_idx = {}
        self.pos_name = ""
        self.pos_idx = 0
        self.sr = 16000
        self.W = 0
        self.S = 0
        self.ring = None
        self.last_fire = 0.0

    # -----------------------------
    # Load checkpoint and build transforms
    # -----------------------------
    @staticmethod
    def _resolve_device(pref: Optional[str]) -> str:
        if pref == "cuda" and torch.cuda.is_available():
            return "cuda"
        if pref == "mps" and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def load_model(self, ckpt_path: str, device: Optional[str] = None):
        ckpt = torch.load(ckpt_path, map_location="cpu")
        labels: List[str] = ckpt["labels"]
        self.cfg = ckpt["cfg"]

        self.dev = self._resolve_device(device or self.cfg.get("device", "cpu"))
        self.model = SmallAudioCNN(self.cfg["n_mels"], len(labels))
        self.model.load_state_dict(ckpt["model"], strict=True)
        self.model.eval().to(self.dev)

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
        self.labels = labels

    # -----------------------------
    # Common feature/infer helpers
    # -----------------------------
    @torch.no_grad()
    def probs_from_waveform(self, x_1xT: torch.Tensor) -> np.ndarray:
        mel = self.melspec(x_1xT)                 # (n_mels, time)
        mel = self.amp2db(mel)
        mel = (mel - mel.mean()) / (mel.std() + 1e-6)
        logits = self.model(mel.unsqueeze(0).to(self.dev)).squeeze(0)  # (n_classes,)
        return torch.softmax(logits, dim=-1).cpu().numpy()

    @staticmethod
    def sliding_windows(x_1xT: torch.Tensor, sr: int, win_s: float, step_s: float):
        W = int(win_s * sr); S = int(step_s * sr); T = x_1xT.shape[1]
        if T < W:
            yield 0, x_1xT
            return
        i = 0
        while i + W <= T:
            yield i, x_1xT[:, i:i+W]
            i += S

    # -----------------------------
    # MIC MODE
    # -----------------------------
    def start_mic(self, 
        model="audio_machine_learning/turn_signal_cnn.pt",
        device=None,
        positive_class=None,
        window_s=1.5,
        step_s=0.25,
        threshold=0.45,
        min_gap_s=1.0,
        on_detect=None,
        on_deactivate=None,
    ):
        import sounddevice as sd

        self.load_model(model, device)
        self.label_to_idx = {n: i for i, n in enumerate(self.labels)}
        self.pos_name = positive_class or ("turn" if "turn" in self.label_to_idx else self.labels[0])
        self.pos_idx = self.label_to_idx[self.pos_name]

        self.sr = self.cfg["sample_rate"]
        self.W = int(window_s * self.sr)
        self.S = int(step_s * self.sr)

        self.ring = torch.zeros(self.W, dtype=torch.float32)
        self.last_fire = 0.0

        self.silence = [] # call on_deactivate after not getting a hit 5 times in a row

        print(f"🎙️ Mic @ {self.sr} Hz | class='{self.pos_name}' thr={threshold}")
        print("Ctrl+C to stop.")

        def callback(indata, frames, time_info, status):
            # nonlocal ring, last_fire
            if status:
                pass
                # print(status, flush=True)
            x = torch.from_numpy(indata.copy()).float()
            if x.ndim == 2:
                x = x.mean(dim=1)
            if x.numel() < self.S:
                return
            self.ring = torch.roll(self.ring, -self.S)
            self.ring[-self.S:] = x[:self.S]

            p = self.probs_from_waveform(self.ring.unsqueeze(0))[self.pos_idx]
            print(f"p({self.pos_name})={p:.2f}", end="\r")
            now = time.time()
            if p >= threshold and (now - self.last_fire) >= min_gap_s:
                self.last_fire = now
                print(f"\n🔔 Detected {self.pos_name} (p={p:.2f}) at {time.strftime('%H:%M:%S')}")
                self.silence = []
                if on_detect:
                    on_detect(p, now)
            else:
                self.silence.append(p)
                if len(self.silence) > 5:
                    self.silence = []
                    if on_deactivate:
                        on_deactivate(now)

        self.stream = sd.InputStream(
            samplerate=self.sr, 
            channels=1, 
            blocksize=self.S, 
            callback=callback
        )
        self.stream.start()

    
    def stop_mic(self):
        self.stream.stop()
        self.stream.close()
        self.stream = None