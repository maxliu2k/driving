import sys
from PIL import Image
import pytesseract
import numpy as np
import cv2
from rapidfuzz import fuzz
from paddleocr import PaddleOCR


import easyocr


def extract_text(test_frame_path: str):

    # Load image with PIL
    frame = cv2.imread(test_frame_path)
    x1, y1, x2, y2 = 1593, 173, 1759, 365
    #cropped = frame[y1:y2, x1:x2]     
    cropped = cv2.imread('testing-signs/cropped.jpg')
    #cropped = cv2.imread('testing-signs/cropped_textread.jpg')
    #cropped = cv2.imread('testing-signs/8757_0000.jpg')
    #cv2.imwrite('testing-signs/cropped2.jpg', cropped)
    #cv2.imshow("cropped sign", cropped)
    #cv2.waitKey(0) 

    # Initialize PaddleOCR model
    #ocr = PaddleOCR(use_textline_orientation=True, lang='en')
    #result = ocr.predict(cropped)
    #for line in result[0]:
    #    text = line[1][0]
    #    #confidence = line[1][1]
    #    print(f"PaddleOCR: '{text}' with confidence")


    #easyocr
    reader = easyocr.Reader(['en'])
    results = reader.readtext(cropped)
    all_lowercase_text = ' '.join([text for (_, text, _) in results]).lower()
    print(f"===========================Extracted sign words using EasyOcr: {all_lowercase_text}")
    if 'speed' in all_lowercase_text and 'limit' in all_lowercase_text:  
        print ('Detected Speed Limit Sign')


    #pytesseract
    #gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    #gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    #_, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    #processed = cv2.medianBlur(thresh, 3)
    #config = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    #all_lowercase_text = pytesseract.image_to_string(cropped, config=config).lower()
    #print(f"===========================Extracted sign words using pytesseract: {all_lowercase_text}")
    #words = all_lowercase_text.split()                                              
    #target_words = ['speed', 'limit']
    #found_targets = {target: False for target in target_words}
    # Check each word in OCR result against each target word
    #for word in words:
    #    for target in target_words:
    #        if not found_targets[target] and fuzz.ratio(word, target) > 0.8:
    #            found_targets[target] = True

        
    #if found_targets['speed'] and found_targets['limit']:  
    #    print ('Detected Speed Limit Sign')


if __name__ == "__main__":

    test_frame_path = 'testing-signs/frame.jpg'

    try:
        extract_text(test_frame_path)
    except FileNotFoundError:
        print(f"Error: The file {test_frame_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)