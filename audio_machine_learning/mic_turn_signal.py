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


# -----------------------------
# Load checkpoint and build transforms
# -----------------------------
def _resolve_device(pref: Optional[str]) -> str:
    if pref == "cuda" and torch.cuda.is_available():
        return "cuda"
    if pref == "mps" and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def load_model(ckpt_path: str, device: Optional[str] = None):
    ckpt = torch.load(ckpt_path, map_location="cpu")
    labels: List[str] = ckpt["labels"]
    cfg = ckpt["cfg"]

    dev = _resolve_device(device or cfg.get("device", "cpu"))
    model = SmallAudioCNN(cfg["n_mels"], len(labels))
    model.load_state_dict(ckpt["model"], strict=True)
    model.eval().to(dev)

    # mel/db params must match training
    f_min = cfg.get("f_min", 20.0)
    f_max = cfg.get("f_max", cfg["sample_rate"] // 2)
    melspec = torchaudio.transforms.MelSpectrogram(
        sample_rate=cfg["sample_rate"],
        n_fft=cfg["n_fft"],
        hop_length=cfg["hop_length"],
        n_mels=cfg["n_mels"],
        power=2.0,
        center=True,
        f_min=f_min,
        f_max=f_max,
    )
    amp2db = torchaudio.transforms.AmplitudeToDB(stype="power")

    return model, labels, cfg, melspec, amp2db, dev


# -----------------------------
# Robust file loader: (1) soundfile, (2) torchaudio, (3) pydub/ffmpeg
# Returns (1, T) float32 [-1,1] and sr==target_sr
# -----------------------------
def safe_load_audio(path: str, target_sr: int) -> Tuple[torch.Tensor, int]:
    ext = Path(path).suffix.lower()

    # 1) soundfile (best for wav/flac; no ffmpeg needed)
    if _HAVE_SF and ext in {".wav", ".flac", ".ogg"}:
        data, sr = sf.read(path, dtype="float32", always_2d=False)
        if data.ndim == 2:
            data = data.mean(axis=1)
        wav = torch.from_numpy(data).unsqueeze(0)
        if sr != target_sr:
            wav = torchaudio.functional.resample(wav, sr, target_sr)
            sr = target_sr
        return wav.contiguous(), sr

    # 2) torchaudio
    try:
        wav, sr = torchaudio.load(path)
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        if sr != target_sr:
            wav = torchaudio.functional.resample(wav, sr, target_sr)
            sr = target_sr
        return wav.to(torch.float32).contiguous(), sr
    except Exception:
        pass

    # 3) pydub (mp3/aac/etc.; needs ffmpeg)
    if _HAVE_PYDUB:
        seg = AudioSegment.from_file(path)
        sr = seg.frame_rate
        ch = seg.channels
        sw = seg.sample_width
        arr = np.array(seg.get_array_of_samples())
        if ch > 1:
            arr = arr.reshape(-1, ch).mean(axis=1)
        wav = torch.from_numpy(arr.astype(np.float32) / float(2 ** (8 * sw - 1))).unsqueeze(0)
        if sr != target_sr:
            wav = torchaudio.functional.resample(wav, sr, target_sr)
            sr = target_sr
        return wav.contiguous(), sr

    raise RuntimeError("Could not decode audio. Install `soundfile` for WAV/FLAC or `pydub`+ffmpeg for MP3.")


# -----------------------------
# Common feature/infer helpers
# -----------------------------
@torch.no_grad()
def probs_from_waveform(model, dev, x_1xT: torch.Tensor, melspec, amp2db) -> np.ndarray:
    mel = melspec(x_1xT)                 # (n_mels, time)
    mel = amp2db(mel)
    mel = (mel - mel.mean()) / (mel.std() + 1e-6)
    logits = model(mel.unsqueeze(0).to(dev)).squeeze(0)  # (n_classes,)
    return torch.softmax(logits, dim=-1).cpu().numpy()

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
# FILE MODE
# -----------------------------
def run_on_file(args):
    model, labels, cfg, melspec, amp2db, dev = load_model(args.model, args.device)
    label_to_idx = {n: i for i, n in enumerate(labels)}
    pos_name = args.positive_class or ("turn" if "turn" in label_to_idx else labels[0])
    pos_idx = label_to_idx[pos_name]

    wav, _ = safe_load_audio(args.file, cfg["sample_rate"])

    hits = []
    last_t = -1e9
    for start, chunk in sliding_windows(wav, cfg["sample_rate"], args.window_s, args.step_s):
        p = probs_from_waveform(model, dev, chunk, melspec, amp2db)[pos_idx]
        t = start / cfg["sample_rate"]
        if p >= args.threshold and (t - last_t) >= args.min_gap_s:
            hits.append((t, p)); last_t = t

    print(f"File: {args.file}")
    print(f"Class: '{pos_name}'  thr={args.threshold:.2f}  win={args.window_s:.2f}s  step={args.step_s:.2f}s  min_gap={args.min_gap_s:.2f}s")
    if hits:
        for t, p in hits:
            print(f"{t:8.3f}s  {p:.3f}")
    else:
        print("No detections.")


# -----------------------------
# MIC MODE
# -----------------------------
def run_on_mic(args):
    import sounddevice as sd

    model, labels, cfg, melspec, amp2db, dev = load_model(args.model, args.device)
    label_to_idx = {n: i for i, n in enumerate(labels)}
    pos_name = args.positive_class or ("turn" if "turn" in label_to_idx else labels[0])
    pos_idx = label_to_idx[pos_name]

    sr = cfg["sample_rate"]
    W = int(args.window_s * sr)
    S = int(args.step_s * sr)

    ring = torch.zeros(W, dtype=torch.float32)
    last_fire = 0.0

    print(f"🎙️ Mic @ {sr} Hz | class='{pos_name}' thr={args.threshold}")
    print("Ctrl+C to stop.")

    def callback(indata, frames, time_info, status):
        nonlocal ring, last_fire
        if status:
            print(status, flush=True)
        x = torch.from_numpy(indata.copy()).float()
        if x.ndim == 2:
            x = x.mean(dim=1)
        if x.numel() < S:
            return
        ring = torch.roll(ring, -S)
        ring[-S:] = x[:S]

        p = probs_from_waveform(model, dev, ring.unsqueeze(0), melspec, amp2db)[pos_idx]
        print(f"p({pos_name})={p:.2f}", end="\r")
        now = time.time()
        if p >= args.threshold and (now - last_fire) >= args.min_gap_s:
            last_fire = now
            print(f"\n🔔 Detected {pos_name} (p={p:.2f}) at {time.strftime('%H:%M:%S')}")

    with sd.InputStream(samplerate=sr, channels=1, blocksize=S, callback=callback):
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopped.")


# -----------------------------
# CLI
# -----------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Run turn-signal detector on a sound file or the microphone.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", type=str, help="Path to audio file (wav/flac/mp3 etc.).")
    src.add_argument("--mic", action="store_true", help="Use system microphone.")

    p.add_argument("--model", type=str, default="turn_signal_cnn.pt", help="Path to trained checkpoint.")
    p.add_argument("--device", type=str, default=None, choices=[None, "cpu", "cuda", "mps"], help="Force device (defaults sensibly).")

    p.add_argument("--positive_class", type=str, default=None, help="Name of positive class (defaults to 'turn' if present).")
    p.add_argument("--window_s", type=float, default=1.5, help="Sliding window seconds.")
    p.add_argument("--step_s", type=float, default=0.25, help="Sliding step seconds.")
    p.add_argument("--threshold", type=float, default=0.85, help="Probability threshold to trigger a detection.")
    p.add_argument("--min_gap_s", type=float, default=1.0, help="Minimum seconds between detections (debounce).")
    return p.parse_args()


def main():
    args = parse_args()
    if args.file:
        run_on_file(args)
    else:
        run_on_mic(args)


if __name__ == "__main__":
    main()


"""
Example Usage:
- File Mode:
python3 mic_turn_signal.py --file path/to/audio.wav --model turn_signal_cnn.pt
py audio_machine_learning/mic_turn_signal.py --file soundTest/turn/car-blinker-39137.wav --model audio_machine_learning/turn_signal_cnn.pt --threshold 0.4

- Mic Mode:
python3 mic_turn_signal.py --mic --model turn_signal_cnn.pt --window_s 1.5 --step_s 0.25 --threshold 0.4
py audio_machine_learning/mic_turn_signal.py --mic --model audio_machine_learning/turn_signal_cnn.pt --window_s 1.5 --step_s 0.25 --threshold 0.4
"""