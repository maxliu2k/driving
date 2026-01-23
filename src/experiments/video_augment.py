"""
This script takes a video file as input, applies a series of augmentations to each frame, and saves the augmented frames as a new video file.
It uses OpenCV for video processing and augmentation

Supported augmentations:
- nighttime effect
- dusk effect

Potential augmentations:
- fog
- rain

"""

import cv2
import numpy as np
import os
import random

def apply_nighttime_effect(frame):
    """Apply nighttime effect to a frame"""
    # Decrease brightness
    frame = cv2.convertScaleAbs(frame, alpha=0.5, beta=0)

    # Tint towards blue
    blue_tint = np.full(frame.shape, (255, 0, 0), dtype=np.uint8)
    frame = cv2.addWeighted(frame, 0.9, blue_tint, 0.1, 0)

    # Inject noise
    sigma = 10
    noise = np.random.normal(0, sigma, frame.shape).astype(np.float32)
    frame_f = frame.astype(np.float32) + noise
    frame = np.clip(frame_f, 0, 255).astype(np.uint8)

    return frame

def apply_dusk_effect(frame):
    pass


if __name__ == "__main__":
    test_img = cv2.imread("test_img.png")

    augmented_img = apply_nighttime_effect(test_img)


    script_dir = os.path.dirname(os.path.abspath(__file__))


    cv2.imwrite("augmented_img.png", augmented_img)