import os
import shutil
import pandas as pd
from PIL import Image
import zipfile
import random
import cv2
import numpy as np

# Function to crop an image based on YOLOv8 label
selected_go_stop_image_folder = 'D:/TeenSafe/DataSet/Houston_traffic_bulbs_original/selected_go_stop_images_2/'
selected_warning_image_folder = 'D:/TeenSafe/DataSet/Houston_traffic_bulbs_original/selected_warning_images/'
label_folder = 'D:/TeenSafe/DataSet/traffic_lights_dataset/labels/'
output_go_stop_image_folder = 'D:/TeenSafe/DataSet/Houston_traffic_bulbs_original/cropped_go_stop_images_2/'
output_warning_image_folder = 'D:/TeenSafe/DataSet/Houston_traffic_bulbs_original/cropped_warning_images/'


def crop_image(image_folder, image_filename, output_image_folder):
    # Read the image
    image_path = image_folder + image_filename
    label_path = label_folder + image_filename.replace('.jpg', '.txt')
    image_file = cv2.imread(image_path)
    height, width, _ = image_file.shape

    # Read the label file
    with open(label_path, 'r') as label_file:
        labels = label_file.readlines()

    label_number = 0
    # Process each label in the label file
    print(image_filename)
    print(image_filename.replace('.jpg', '.txt'))
    print(width)
    print(height)
    for label in labels:
        class_index, x_center, y_center, bbox_width, bbox_height = map(float, label.split())

        # Convert normalized coordinates to pixel values
        x_center_pixel = int(x_center * width)
        y_center_pixel = int(y_center * height)
        bbox_width_pixel = int(bbox_width * width)
        bbox_height_pixel = int(bbox_height * height)

        # Calculate the top-left corner of the bounding box
        x1 = int(x_center_pixel - bbox_width_pixel / 2)
        y1 = int(y_center_pixel - bbox_height_pixel / 2)
        x2 = int(x_center_pixel + bbox_width_pixel / 2)
        y2 = int(y_center_pixel + bbox_height_pixel / 2)

        
        print('x_center_pixel:' +  str(x_center_pixel))
        print('y_center_pixel:' +  str(y_center_pixel))
        print('bbox_width_pixel:' +  str(bbox_width_pixel))
        print('bbox_height_pixel:' +  str(bbox_height_pixel))
    
        print(f"x1:{x1}")
        print(f"y1:{y1}")
        print(f"x2:{x2}")
        print(f"y2:{y2}")

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)

        if x1 >= x2 or y1 >= y2:
            print("Invalid cropping coordinates; skipping this label.")
            continue  # Skip this label if invalid

        # Crop the image using the bounding box
        cropped_image = image_file[y1:y2, x1:x2]

        label_number = label_number+1


        index = image_filename.find('_jpg')
        cropped_image_filename_withoutextension = 'cropped_' + image_filename[:index]

        print(cropped_image_filename_withoutextension)
        # Save the cropped image with the class index as part of the filename
        output_filename = f"{output_image_folder}/{cropped_image_filename_withoutextension}_{(label_number):02d}.jpg"
        cv2.imwrite(output_filename, cropped_image)


# if(os.path.exists(output_go_stop_image_folder)):
#     shutil.rmtree(output_go_stop_image_folder)
# os.makedirs(output_go_stop_image_folder, exist_ok = True)

# for selected_image_filename in os.listdir(selected_go_stop_image_folder)[::2]:
#     crop_image(selected_go_stop_image_folder, selected_image_filename, output_go_stop_image_folder)


if(os.path.exists(output_warning_image_folder)):
    shutil.rmtree(output_warning_image_folder)
os.makedirs(output_warning_image_folder, exist_ok = True)

for selected_image_filename in os.listdir(selected_warning_image_folder):
    crop_image(selected_warning_image_folder, selected_image_filename, output_warning_image_folder)



##################################################################
# exist_count=0
# not_exist_count=0
# for selected_image_filename in os.listdir(selected_go_stop_image_folder)[::2]:
#     exist=False
#     for filename in os.listdir('D:/TeenSafe/DataSet/Houston_traffic_bulbs_original/cropped_images_20241108/'):
#         if selected_image_filename[:9].lower() in filename.lower():
#             print(f"The file '{selected_image_filename[:9]}' exists in the folder.")
#             exist_count = exist_count + 1
#             exist = True
#             break
    
#     if (exist==False):
#         print(f"The file '{selected_image_filename[:9]}' not exists in the folder.")
#         crop_image(selected_go_stop_image_folder, selected_image_filename)
#         not_exist_count = not_exist_count + 1
# print('exist count is: ' + str(exist_count))
# print('not exist count is: ' + str(not_exist_count))