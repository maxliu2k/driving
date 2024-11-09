import PIL
import cv2

def crop_image(frame, bbox):
    print(f"bbox: {bbox}")
    x, y, w, h = bbox

    # convert to int
    x, y, w, h = int(x), int(y), int(w), int(h)

    return frame[y:y+h, x:x+w]