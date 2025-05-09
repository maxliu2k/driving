import cv2
from ultralytics import YOLO
from utils import *
#import smbus
from time import sleep
import math
import threading
import pytesseract
import re


"""
def update_lights(new_light_data, old_light_data):

    #new_light_data: list of tuples containing (x1, y1, x2, y2, color, light_conf, color_conf, changed)
    #lights_collection: list to store the light data [light_data, light_data, ...]

    new_lights_to_add = [True for _ in range(len(new_light_data))]                   

    # Check if the center of the light is within the bounds of any of the current lights in the list
    for old_light in old_light_data:

        center_x = (old_light[0] + old_light[2]) / 2
        center_y = (old_light[1] + old_light[3]) / 2

        # For light in lights_collection: 
        #     light[7] = -1

        should_remove = True
        for idx, new_light in enumerate(new_light_data):
            if new_light[0] <= center_x <= new_light[2] and new_light[1] <= center_y <= new_light[3]:
                should_remove = False
                new_lights_to_add[idx] = False
                # Update existing light
                new_light_color = new_light[4]

                old_light_data[idx] = new_light

                # Check if current color is different from the old color
                if old_light[4] != new_light_color:
                    old_light_data[idx][7] = True  # Mark as changed

        if should_remove:
            old_light_data.remove(old_light)      
      
    # Add new lights that are not already in the old lights
    for idx, add in enumerate(new_lights_to_add):
        if add:
            old_light_data.append(new_light_data[idx])
        
    return old_light_data
"""


def main():
    conf_threshold=0.7

    #voice = Voice("piper.onnx")
    count = 0

    # Load YOLO model
    #l_model = YOLO('bestlights.pt')
    #b_model = YOLO('bestbulbs.pt')
    s_model = YOLO('bestsigns.pt') 

    # Start video stream
    # cap = cv2.VideoCapture(0)
    # alternatively, use a video file 
    cap = cv2.VideoCapture('videoTest/IMG_8767.mp4')

    # (x1,y1,x2,y2,color,light_conf,color_conf) 
    left_turn_signals = [(0.2,0.2,0.4,0.4,'green',0.9,0.9)] # Example data
    right_turn_signals = [(0.5,0.5,0.7,0.7,'red',0.9,0.9)] # Example data
    forward_signals = [(0.8,0.8,1.0,1.0,'yellow',0.9,0.9)] # Example data

    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        if (count % 5 == 0):
            s_results = s_model(frame)       

            for s_box in s_results[0].boxes:
                x1, y1, x2, y2 = map(int, s_box.xyxy[0])

                # Crop the detected region from the frame
                cropped = frame[y1:y2, x1:x2]

                # Optional: Preprocess the cropped image for better OCR
                #gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                #_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                lowercase_text= pytesseract.image_to_string(cropped).lower()
                if 'speed' in lowercase_text and 'limit' in lowercase_text:

                    # Extract the first number (e.g., 50)
                    match = re.search(r'\b\d{1,2}\b', lowercase_text)
                    if match:
                        speed_value = int(match.group())
                        print(f"Customized Printing - Extracted speed limit: {speed_value}")


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if (count % 5 == 0):
                # Small delay to ease CPU load
                sleep(0.17)  

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()