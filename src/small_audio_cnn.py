import torch
import torch.nn
# ===============================
# Audio Model
# ===============================
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