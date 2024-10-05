import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO('bestlights.pt')

# Start video stream
cap = cv2.VideoCapture(0)

while cap.isOpened():
    # Read video frame
    ret, frame = cap.read()
    if not ret:
        break

    # Perform prediction
    results = model(frame)

    annotated_frame = results[0].plot()

    # Display the frame
    cv2.imshow('Model Test', annotated_frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()