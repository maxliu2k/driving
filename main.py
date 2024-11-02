from voice import Voice
import cv2
from ultralytics import YOLO

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
    s_model = YOLO('bestsigns.pt')

    # Start video stream
    cap = cv2.VideoCapture(0)

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
        s_results = s_model(frame)

        # identify the speed limit in the image


        # React to the analysis

        # TTS for the lights
        # - If stopped at right light that turns green, say "Green"
        
        # simulate the AI finding two new lights
        

        

        # TTS for the speed limit
        # - If car exceeds speed limit, say "Slow down!"

        

    cap.release()


if __name__ == "__main__":
    main()