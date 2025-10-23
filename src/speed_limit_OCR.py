import easyocr
from rapidfuzz import fuzz
import re


# ===============================
# Speed Limit OCR: Uses EasyOCR to detect and extract speed limit values.
# ===============================
class SpeedLimitOCR:
    # Initialize EasyOCR reader with the given language list.
    def __init__(self, language_list):
        self.reader = easyocr.Reader(language_list)

    # Detect and extract the speed limit number.
    def extract_speed_limit(self, frame, conf_threshold):
        speed_limit_value = None
        target_words = ['speed', 'limit']
        found_targets = {target: False for target in target_words}

        # OCR detection
        results = self.reader.readtext(frame)
        all_lowercase_text = ' '.join([text for (_, text, _) in results]).lower()

        # Check if "speed" and "limit" appear in OCR text
        for _, text, _ in results:
            for target in target_words:
                if not found_targets[target] and fuzz.ratio(text.lower(), target) > conf_threshold:
                    found_targets[target] = True

        # Extract numeric value if both words are found
        if found_targets['speed'] and found_targets['limit']:
            match = re.search(r'\b\d{2}\b', all_lowercase_text)
            if match:
                speed_limit_value = int(match.group())

        return speed_limit_value
    
    
    
import cv2
def main():
    # Initialize video capture
    cap = cv2.VideoCapture('tests/video/Demo_1080.mp4')
    ocr_manager = SpeedLimitOCR(['en'])

    best_speed_limit_value = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Example: manually define ROI for OCR (replace with dynamic bounding box in your case)
        x1, y1, x2, y2 = 100, 100, 300, 300  
        cropped = frame[y1:y2, x1:x2]

        speed_limit_value, found_targets = ocr_manager.extract_speed_limit(cropped, 0.8)

        if found_targets['speed'] and found_targets['limit']:
            print(f"Detected speed limit: {speed_limit_value} mph")

            # Store the best detected value (example logic)
            if speed_limit_value > best_speed_limit_value:
                best_speed_limit_value = speed_limit_value

        # Display frame for visual debugging
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"Speed Limit: {best_speed_limit_value}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("OCR Speed Limit Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()