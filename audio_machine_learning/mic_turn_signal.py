import argparse, torch, torchaudio, numpy as np
from pydub import AudioSegment
import torch.nn as nn

class SmallAudioCNN(nn.Module):
    def __init__(self, n_mels, n_classes):
        super().__init__()
        self.features=nn.Sequential(
            nn.Conv2d(1,32,3,padding=1),nn.BatchNorm2d(32),nn.ReLU(),
            nn.Conv2d(32,32,3,padding=1),nn.BatchNorm2d(32),nn.ReLU(),nn.MaxPool2d(2),
            nn.Conv2d(32,64,3,padding=1),nn.BatchNorm2d(64),nn.ReLU(),
            nn.Conv2d(64,64,3,padding=1),nn.BatchNorm2d(64),nn.ReLU(),nn.MaxPool2d(2),
            nn.Conv2d(64,128,3,padding=1),nn.BatchNorm2d(128),nn.ReLU(),
            nn.Conv2d(128,128,3,padding=1),nn.BatchNorm2d(128),nn.ReLU(),
            nn.AdaptiveAvgPool2d((1,1)))
        self.classifier=nn.Sequential(nn.Flatten(),nn.Linear(128,64),nn.ReLU(),nn.Dropout(0.2),nn.Linear(64,n_classes))
    def forward(self,x):
        x=self.features(x)
        x=self.classifier(x)
        return x

def load_model(path, device):
    checkpoint = torch.load(path, map_location=device)
    labels = checkpoint['labels']
    config = checkpoint['cfg']
    model = SmallAudioCNN(config["n_mels"], len(labels))
    model.load_state_dict(checkpoint['model'])
    model.to(device).eval()
    mel_spectrogram = torchaudio.transforms.MelSpectrogram(
        sample_rate=config["sample_rate"], n_mels=config["n_mels"],
        n_fft=config["n_fft"], hop_length=config["hop_length"],
        power=2.0, center=True, f_min=20.0, f_max=config["sample_rate"] // 2
    ).to(device)
    decibels = torchaudio.transforms.AmplitudeToDB(stype="power")
    return model, labels, config, mel_spectrogram, decibels

def load_mp3(path_str, sample_rate):
    seg=AudioSegment.from_file(path_str)
    channels = seg.channels
    sample_width = seg.sample_width
    frame_rate = seg.frame_rate
    samples = np.array(seg.get_array_of_samples()).astype(np.float32)
    if channels > 1:
        samples = samples.reshape((-1, channels)).mean(axis=1)
    # normalize to [-1, 1]
    wav = torch.from_numpy(samples/(2**(8*sample_width-1))).unsqueeze(0)
    if frame_rate != sample_rate:
        wav = torchaudio.functional.resample(wav, frame_rate, sample_rate)
    return wav

@torch.no_grad()
def run(file,model,labels,cfg,ms,db,dev,cls,win_s,step_s,thr):
    idx={n:i for i,n in enumerate(labels)}.get(cls or ("turn" if "turn" in labels else labels[0]))
    sr=cfg["sample_rate"]; W=int(win_s*sr); S=int(step_s*sr); x=load_mp3(file,sr)
    T=x.shape[1]; i=0; hits=[]
    while i+W<=T:
        mel=ms(x[:,i:i+W]); mel=db(mel); mel=(mel-mel.mean())/(mel.std()+1e-6)
        p=torch.softmax(model(mel.unsqueeze(0).to(dev)).squeeze(0),-1)[idx].item()
        if p>=thr: hits.append((i/sr,p))
        i+=S
    print(file)
    if hits:
        for t,p in hits: print(f"{t:.3f}s {p:.3f}")
    else:
        print("no detections")

if __name__ == "__main__":
    input_file = "soundTest/turn-signal.mp3"
    model, labels, cfg, ms, db = load_model("audio_machine_learning/turn_signal_cnn.pt", torch.device("cpu"))
    run(input_file, model, labels, cfg, ms, db, torch.device("cpu"), "turn", 1.0, 0.1, 0.5)