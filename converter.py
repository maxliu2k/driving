import torch
from torch.utils.mobile_optimizer import optimize_for_mobile
from ultralytics import YOLO

# Load your custom model
model = YOLO('bestsigns.pt')
# Export directly to TorchScript format (this will optimize the model as well)
model.export(format="torchscript", optimize=True)