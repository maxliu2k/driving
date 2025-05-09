import sys
from PIL import Image
import pytesseract

def extract_text(image_path: str) -> str:
    img = Image.open('testing-signs/8757_0000.jpg')
    return pytesseract.image_to_string(img)

if __name__ == "__main__":
    test_image_path = "speed_limit_test.png"

    try:
        text = extract_text(test_image_path)
        print("Extracted Text:")
        print(text)
    except FileNotFoundError:
        print(f"Error: The file {test_image_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)