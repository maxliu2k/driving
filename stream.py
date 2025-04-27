import cv2
from ultralytics import YOLO
from utils import *
from time import sleep
import math
import threading

def speak_async(voice, text):
    threading.Thread(target=voice.speak, args=(text,), daemon=True).start()

def main():
    count = 0
    # Load YOLO model
    l_model = YOLO('bestlights_temp.pt')
    # s_model = YOLO('bestsigns.pt') 
    b_model = YOLO('bestbulbs.pt')

    # Start video stream
    # cap = cv2.VideoCapture(0)

    # alternatively, use a video file 
    cap = cv2.VideoCapture('videoTest/IMG_1412.MOV')

    # (x1,y1,x2,y2,color,light_conf,color_conf) 
    left_turn_signals = [(0.2,0.2,0.4,0.4,'green',0.9,0.9)] # Example data
    right_turn_signals = [(0.5,0.5,0.7,0.7,'red',0.9,0.9)] # Example data
    forward_signals = [(0.8,0.8,1.0,1.0,'yellow',0.9,0.9)] # Example data

    red = False

    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        if (count % 5 == 0):
            # ---------------------------------
            # Get accelerometer data
            # ---------------------------------
            # print(f"Accel -> Direction: {direction}, Accel: {accel_magnitude:.2f}, "
            #     f"Ax: {(Ax+Ax_offset):.2f}, Ay: {(Ay+Ay_offset):.2f}, Az: {(Az+Az_offset):.2f}")
            
            # identify traffic signs in the image
            # s_results = s_model(frame) 

            # ---------------------------------
            # Traffic Lights Detection via YOLO
            # ---------------------------------
            l_results = l_model(frame)  # Detect traffic lights
            annotated_frame = l_results[0].plot()
            identified_lights = []

            for l_result in l_results[0].boxes:
                # check confidence
                if l_result.conf > 0.5:
                    # print(result)

                    # extract the bounding box coordinates
                    x, y, w, h = l_result.xywh[0]
                    # print("IMAGE COORDINATES")
                    # print(x, y, w, h)


                    # crop the image to the traffic light
                    cropped_frame = crop_image(frame, (x - w/2, y - h/2, w, h))

                    # for debugging, save the cropped image as a file
                    # cv2.imwrite("cropped.jpg", cropped_frame) 

                    # also save the original frame annotated with the bounding box
                    # cv2.imwrite("annotated.jpg", annotated_frame)

                    # identify the bulb color in the image
                    b_results = b_model(cropped_frame)
                    # print(b_results)

                    # format the data for the update_lights function
                    for box in b_results[0].boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        id = int(box.cls[0].cpu().numpy())
                        color = b_results[0].names[id]
                        color_conf = box.conf[0]
                        light_conf = l_result.conf[0]
                        identified_lights.append((x1, y1, x2, y2, color, light_conf, color_conf, False))
                        print("=====================================================")
                        print(f"Detected color: {color} with confidence {color_conf}")

                        cv2.imshow("Bulb Frame", b_results[0].plot())
            
            # Update the lights collection with new detections
            # lights_collection = update_lights(identified_lights, lights_collection) 
            # print(f"Updated Lights Collection: {lights_collection}") 
            lights_collection = identified_lights
            
            # ---------------------------------
            # Trigger Voice Feedback Based on Analysis
            # ---------------------------------
            
            temp = red
            for idx, light in enumerate(lights_collection):
                # if light[7] and light[4].lower() == 'green' and direction == "Stationary":
                    # voice.speak("Green")
                    # # Reset the changed flag after speaking
                    # updated = list(light)
                    # updated[7] = False
                    # lights_collection[idx] = tuple(updated)
                if (light[4].lower() == "stop"):
                    red = True 
            
            # Example: if moving forward with high acceleration (indicating speeding), warn to slow down
            # if direction == "Forward" and accel_magnitude > 1.5:
            #     voice.speak("Slow down!")

            # # identify the speed limit in the image

            # # React to the analysis

            # # TTS for the lights
            # # - If stopped at right light that turns green, say "Green"
            # if False:
            #     voice.speak('Green') 
            
            # # simulate the AI finding two new lights
            # new_lights = [(0.1,0.1,0.3,0.3,'green',0.9,0.9, False), (0.4,0.4,0.6,0.6,'red',0.9,0.9, False)]

            # # TTS for the speed limit
            # # - If car exceeds speed limit, say "Slow down!"

            # ---------------------------------
            # Display the annotated frame
            # ---------------------------------
            cv2.imshow("Annotated Frame", annotated_frame)
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if (count % 5 == 0):
                sleep(0.17)  # Small delay to ease CPU load
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()