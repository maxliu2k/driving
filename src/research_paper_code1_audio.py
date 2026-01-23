import torch
import torchaudio
from torch.utils.data import Dataset, DataLoader
import os
import json

# ===============================
# Audio Model
# ===============================

# Create CNN architecture
class SmallAudioCNN(torch.nn.Module):
    def __init__(self, n_mels: int, n_classes: int):
        super().__init__()
        self.features = torch.nn.Sequential(
            torch.nn.Conv2d(1, 32, 3, padding=1), torch.nn.BatchNorm2d(32), torch.nn.ReLU(),
            torch.nn.Conv2d(32, 32, 3, padding=1), torch.nn.BatchNorm2d(32), torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),

            torch.nn.Conv2d(32, 64, 3, padding=1), torch.nn.BatchNorm2d(64), torch.nn.ReLU(),
            torch.nn.Conv2d(64, 64, 3, padding=1), torch.nn.BatchNorm2d(64), torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),

            torch.nn.Conv2d(64, 128, 3, padding=1), torch.nn.BatchNorm2d(128), torch.nn.ReLU(),
            torch.nn.Conv2d(128, 128, 3, padding=1), torch.nn.BatchNorm2d(128), torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(128, 64), torch.nn.ReLU(), torch.nn.Dropout(0.2),
            torch.nn.Linear(64, n_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))


# Create Dataset Class
class TurnSignalSoundDataset(Dataset):
    def __init__(self, root_dir, cfg, labels):
        self.root_dir = root_dir
        self.labels = labels
        self.cfg = cfg  # Store cfg for use in __getitem__
        self.filepaths = []

        for label in labels:
            label_path = os.path.join(root_dir, label)
            for fname in os.listdir(label_path):
                if fname.endswith(".wav"):
                    self.filepaths.append((os.path.join(label_path, fname), label))

        self.label_to_idx = {label: idx for idx, label in enumerate(labels)}

        self.melspec = torchaudio.transforms.MelSpectrogram(
            sample_rate=cfg["sample_rate"],
            n_fft=cfg["n_fft"],
            hop_length=cfg["hop_length"],
            n_mels=cfg["n_mels"]
        )
        self.amp2db = torchaudio.transforms.AmplitudeToDB(stype="power")

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        filepath, label = self.filepaths[idx]
        waveform, sr = torchaudio.load(filepath)

        if sr != self.cfg["sample_rate"]:
            waveform = torchaudio.functional.resample(waveform, sr, self.cfg["sample_rate"])

        mel = self.melspec(waveform)
        mel_db = self.amp2db(mel)

        # Add channel dimension for CNN (C=1)
        if mel_db.ndim == 2:
            mel_db = mel_db.unsqueeze(0)

        return mel_db, self.label_to_idx[label]


def main():
    # Define Configuration
    cfg = {
        "sample_rate": 16000,
        "n_fft": 1024,
        "hop_length": 512,
        "n_mels": 64,
        "batch_size": 8,
        "epochs": 20,
        "learning_rate": 1e-3,
        "f_min": 20.0,
        "f_max": 8000.0,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
    }

    labels = ["noise", "turn"]

    # Create datasets and loaders
    train_dataset = TurnSignalSoundDataset("data/train", cfg, labels)
    val_dataset = TurnSignalSoundDataset("data/val", cfg, labels)

    train_loader = DataLoader(train_dataset, batch_size=cfg["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=cfg["batch_size"])

    # Initialize model
    n_classes = len(labels)
    model = SmallAudioCNN(cfg["n_mels"], n_classes).to(cfg["device"])

    # Loss and optimizer
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["learning_rate"])

    # Train and validate
    for epoch in range(cfg["epochs"]):
        # Training
        model.train()
        total_loss, total_correct = 0, 0

        for mel, label in train_loader:
            mel, label = mel.to(cfg["device"]), label.to(cfg["device"])

            optimizer.zero_grad()
            output = model(mel)
            loss = criterion(output, label)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            total_correct += (output.argmax(1) == label).sum().item()

        train_acc = total_correct / len(train_loader.dataset)
        print(f"Epoch {epoch+1}/{cfg['epochs']} Train Loss: {total_loss:.3f} Train Acc: {train_acc:.3f}")

        # Validation
        model.eval()
        val_correct, val_loss = 0, 0
        with torch.no_grad():
            for mel, label in val_loader:
                mel, label = mel.to(cfg["device"]), label.to(cfg["device"])
                output = model(mel)
                loss = criterion(output, label)

                val_loss += loss.item()
                val_correct += (output.argmax(1) == label).sum().item()

        val_acc = val_correct / len(val_loader.dataset)

    # Save model to specified path
    os.makedirs("models/sound", exist_ok=True)
    torch.save({
        "model": model.state_dict(),
        "labels": labels,
        "cfg": cfg
    }, os.path.join("models", "sound", "turn_signal_cnn.pt"))

if __name__ == "__main__":
    main()
