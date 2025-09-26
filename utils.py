import PIL
import cv2

def crop_image(frame, bbox):
    x, y, w, h = bbox

    # Convert to int
    x, y, w, h = int(x), int(y), int(w), int(h)

    return frame[y:y+h, x:x+w]