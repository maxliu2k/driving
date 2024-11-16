from voice import Voice
import cv2
from ultralytics import YOLO
from utils import *

def update_lights(new_light_data, old_light_data):
    """
    new_light_data: list of tuples containing (x1, y1, x2, y2, color, light_conf, color_conf, changed)
    lights_collection: list to store the light data [light_data, light_data, ...]
    """

    new_lights_to_add = [True for _ in range(len(new_light_data))]
                      # [action for object in container if condition]

    # check if the center of the light is within the bounds of any of the current lights in the list
    for old_light in old_light_data:

        center_x = (old_light[0] + old_light[2]) / 2
        center_y = (old_light[1] + old_light[3]) / 2

        # for light in lights_collection:
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

def main():
    voice = Voice()

    # Load YOLO model
    l_model = YOLO('bestlights.pt')
    # s_model = YOLO('bestsigns.pt')
    b_model = YOLO('bestbulbs.pt')

    # Start video stream
    cap = cv2.VideoCapture(0)

    # alternatively, use a video file
    #cap = cv2.VideoCapture('videos/IMG_1412.MOV')

    voice.speak("Recording started!")

    # (x1,y1,x2,y2,color,light_conf,color_conf)
    left_turn_signals = [(0.2,0.2,0.4,0.4,'green',0.9,0.9)] # Example data
    right_turn_signals = [(0.5,0.5,0.7,0.7,'red',0.9,0.9)] # Example data
    forward_signals = [(0.8,0.8,1.0,1.0,'yellow',0.9,0.9)] # Example data

    while cap.isOpened():
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break

        # Perform prediction
        l_results = l_model(frame) # Find the traffic lights in frame
        # identify if the lights found are green, red, yellow, or some combination

        # identify traffic signs in the image
        # s_results = s_model(frame)

        identified_lights = []

        # iterate through all the traffic lights found
        annotated_frame = l_results[0].plot()
        for result in l_results[0].boxes:
            # check confidence
            if result.conf > 0.5:
                print(result)

                # extract the bounding box coordinates
                x, y, w, h = result.xywh[0]
                # print("IMAGE COORDINATES")
                # print(x, y, w, h)


                # crop the image to the traffic light
                cropped_frame = crop_image(frame, (x, y, w, h))

                # for debugging, save the cropped image as a file
                # cv2.imwrite("cropped.jpg", cropped_frame)

                # also save the original frame annotated with the bounding box
                # cv2.imwrite("annotated.jpg", annotated_frame)

                # identify the bulb color in the image
                b_results = b_model(cropped_frame)
                # print(b_results)

                # format the data for the update_lights function
                x1, y1, x2, y2 = result.xyxy[0]
                color = b_results[0].names[0]
                light_conf = result.conf
                color_conf = b_results[0].conf
                identified_lights.append((x1, y1, x2, y2, color, light_conf, color_conf, False))
        
        print(f"Identified lights: {identified_lights}")

        
        # show the annotated frame
        # cv2.imshow("Annotated Frame", annotated_frame)
        # # Exit on 'q' key press
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

                
                


        # identify the speed limit in the image


        # React to the analysis

        # TTS for the lights
        # - If stopped at right light that turns green, say "Green"
        if False:
            voice.speak('Green')
        
        # simulate the AI finding two new lights
        new_lights = [(0.1,0.1,0.3,0.3,'green',0.9,0.9, False), (0.4,0.4,0.6,0.6,'red',0.9,0.9, False)]

        

        # TTS for the speed limit
        # - If car exceeds speed limit, say "Slow down!"

        

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()