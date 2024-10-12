from voice import Voice
import cv2
from ultralytics import YOLO


def main():
    voice = Voice()

    # Load YOLO model
    l_model = YOLO('bestlights.pt')
    s_model = YOLO('bestsigns.pt')

    # Start video stream
    cap = cv2.VideoCapture(0)

    voice.speak("Recording started!")

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

        # TTS for the speed limit
        # - If car exceeds speed limit, say "Slow down!"

        

    cap.release()


if __name__ == "__main__":
    main()