import sys
from PIL import Image
import pytesseract
import numpy as np
import cv2
from rapidfuzz import fuzz
from paddleocr import PaddleOCR


import easyocr

"""
Experiment:
- run both pytesseract and easyocr on the unmodified set of images and print the results
- run both on modified images and print results
"""


clear_image = "videoTest/TrafficSigns/cropped_speed_limit_sign_70.jpg" # SPEED LIMIT 50 
blurred_image = "videoTest/TrafficSigns/cropped_speed_limit_sign_5.jpg" # SPEED LIMIT 50 
blurred_image2 = "videoTest/TrafficSigns/cropped_speed_limit_sign_100.jpg" # SPEED LIMIT 50 
blurred_image3 = "videoTest/TrafficSigns/cropped_speed_limit_sign_200.jpg" # SPEED LIMIT 50 
blurred_image4 = "videoTest/TrafficSigns/cropped_speed_limit_sign_215.jpg" # SPEED LIMIT 45 
blurred_image5 = "videoTest/TrafficSigns/cropped_speed_limit_sign_270.jpg" # SPEED LIMIT 45 

images = [
    (clear_image, "SPEED LIMIT 50"),
    (blurred_image, "SPEED LIMIT 50"),
    (blurred_image2, "SPEED LIMIT 50"),
    (blurred_image3, "SPEED LIMIT 50"),
    (blurred_image4, "SPEED LIMIT 45"),
    (blurred_image5, "SPEED LIMIT 45"),
]


def preprocess_sign(img: np.ndarray, upscale=True, grayscale=True, denoise=True, threshold=True, morph=True, sharpen=True) -> np.ndarray:
    # Upscale the image
    if upscale:
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # Convert to grayscale
    if grayscale:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(gray)

    # Denoise the image
    if denoise:
        img = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # Apply thresholding
    if threshold:
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, blockSize=31, C=10)

    # morphological closing
    if morph:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=1)

    # sharpen the image
    if sharpen:
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, sharpen_kernel)

    return img

# initialize the readers
easy_reader = easyocr.Reader(['en'])
tess_config = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def run_easyocr(img: np.ndarray) -> str:
    results = easy_reader.readtext(img, batch_size=4)
    return ' '.join([text for (_, text, _) in results]).strip()

def run_pytesseract(img: np.ndarray) -> str:
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    return pytesseract.image_to_string(gray, config=tess_config).strip()

def experiment():
    overall_start_time = cv2.getTickCount()
    for img_path, expected_text in images:
        print(f"Processing image: {img_path}")
        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Could not read image {img_path}")
            continue
        preprocessed_img = preprocess_sign(img, upscale=True, grayscale=True, denoise=False, threshold=True, morph=True, sharpen=True)

        start_time = cv2.getTickCount()

        # Save the preprocessed image for debugging
        new_path = img_path.replace('.jpg', '_preprocessed.jpg')
        cv2.imwrite(f'{new_path}', preprocessed_img)
        easy_text_og = run_easyocr(img)
        # tess_text_og = run_pytesseract(img)
        easy_text = run_easyocr(preprocessed_img)
        # tess_text = run_pytesseract(preprocessed_img)
        print(f"Expected: {expected_text}")
        print(f"Original EasyOCR: {easy_text_og}")
        # print(f"Original Tesseract: {tess_text_og}")
        print(f"EasyOCR: {easy_text}")
        # print(f"Tesseract: {tess_text}")

        end_time = cv2.getTickCount()
        time_taken = (end_time - start_time) / cv2.getTickFrequency()
        print(f"Time taken: {time_taken:.2f} seconds\n")
    
    overall_end_time = cv2.getTickCount()
    overall_time_taken = (overall_end_time - overall_start_time) / cv2.getTickFrequency()
    print(f"Overall time taken for all images: {overall_time_taken:.2f} seconds")


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
        print ('Detected SPEED LIMIT Sign')


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
    #    print ('Detected SPEED LIMIT Sign')


if __name__ == "__main__":

    try:
        experiment()
    except Exception as e:
        print(f"An error occurred during the experiment: {e}")
        sys.exit(1)


    # test_frame_path = 'testing-signs/frame.jpg'

    # try:
    #     extract_text(test_frame_path)
    # except FileNotFoundError:
    #     print(f"Error: The file {test_frame_path} was not found.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     sys.exit(1)



#     (venv) PS C:\Users\maxli\Driving> py text_read.py
# Neither CUDA nor MPS are available - defaulting to CPU. Note: This module is much faster with a GPU.
# Processing image: videoTest/TrafficSigns/cropped_speed_limit_sign_70.jpg
# Expected: SPEED LIMIT 50
# Original EasyOCR: SPEED LIMIT 50
# EasyOCR: SPEED LIMITL 5
# Time taken: 1.29 seconds

# Processing image: videoTest/TrafficSigns/cropped_speed_limit_sign_5.jpg
# Expected: SPEED LIMIT 50
# Original EasyOCR: SPEED Limit 50
# EasyOCR: SPEED LIMiTI 50
# Time taken: 0.49 seconds

# Processing image: videoTest/TrafficSigns/cropped_speed_limit_sign_100.jpg
# Expected: SPEED LIMIT 50
# Original EasyOCR: SPELD 50
# EasyOCR: SPtD Lixit 50
# Time taken: 0.39 seconds

# Processing image: videoTest/TrafficSigns/cropped_speed_limit_sign_200.jpg
# Expected: SPEED LIMIT 50
# Original EasyOCR: 50
# EasyOCR: srtc3 UVJT 50
# Time taken: 0.24 seconds

# Processing image: videoTest/TrafficSigns/cropped_speed_limit_sign_215.jpg
# Expected: SPEED LIMIT 45
# Original EasyOCR: 
# EasyOCR: 35
# Time taken: 0.16 seconds

# Processing image: videoTest/TrafficSigns/cropped_speed_limit_sign_270.jpg
# Expected: SPEED LIMIT 45
# Original EasyOCR: U4n 45
# EasyOCR: Pe SPIDD uXM, 45
# Time taken: 0.46 seconds

# Overall time taken for all images: 3.04 seconds