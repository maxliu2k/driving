import PIL
import cv2
from typing import Optional
import torch

def crop_image(frame, bbox):
    x, y, w, h = bbox

    # Convert to int
    x, y, w, h = int(x), int(y), int(w), int(h)

    return frame[y:y+h, x:x+w]


def resolve_device(pref: Optional[str] = None) -> str:
    """
    Resolve which device to use for computation.

    Args:
        pref: Optional preference string: "cuda", "mps", "xla", or None.

    Returns:
        str: device name ("cuda", "mps", "xla", or "cpu").
    """
    if pref == "cuda" and torch.cuda.is_available():
        return "cuda"
    if pref == "mps" and torch.backends.mps.is_available():
        return "mps"
    if pref == "xla":  # TPU
        return "xla"
    return "cpu"