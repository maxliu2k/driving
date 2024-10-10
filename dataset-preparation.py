import os
import shutil
import pandas as pd
from PIL import Image
import zipfile

# enter model name
model_name='traffic_lights'

lisa_unzip_path='D:/TeenSafe/DataSet/LISA_'+ model_name + '_original/'
lisa_annotations_base_path = lisa_unzip_path+ 'Annotations/'
lisa_full_images_path ='D:/TeenSafe/DataSet/LISA_'+ model_name + '_full/images/'
lisa_full_labels_path ='D:/TeenSafe/DataSet/LISA_'+ model_name + '_full/labels/'
dataset_base_path ='D:/TeenSafe/DataSet/' + model_name + '_dataset/'
dataset_images_path = dataset_base_path + 'images/'
dataset_labels_path = dataset_base_path + 'labels/'
dataset_zipfile_name = dataset_base_path.split('/')[-2] + '.zip'
dataset_zipfile_path = dataset_base_path + dataset_zipfile_name
dataset_zipfile_google_drive_path = 'G:/My Drive/Colab Notebooks/' + model_name + '/' + dataset_zipfile_name


# Process LISA traffic lights annotation
def process_lisa_traffic_lights_annotation(csv_path):
        
        class_mapping = {'stop': 0, 'stopLeft': 1, 'go': 2, 'goLeft': 3, 'warning': 4, 'warningLeft':5, 'goForward': 6}
        
        annotations = pd.read_csv(csv_path, delimiter=';')
        print(csv_path)
        # process each CSV row
        for _, row in annotations.iterrows():
            image_file_name = row["Filename"]
            class_name = row["Annotation tag"]

            # check if class exists
            if class_name not in class_mapping:
                continue

            image_path = os.path.join(lisa_full_images_path, image_file_name.split('/')[-1])
            if not os.path.exists(image_path):
                continue

            with Image.open(image_path) as img:
                width, height = img.size

            # Get YOLO values
            class_idx = class_mapping[class_name]
            x = (row["Upper left corner X"] + row["Lower right corner X"]) / 2.0 / width
            y = (row["Upper left corner Y"] + row["Lower right corner Y"]) / 2.0 / height
            w = (row["Lower right corner X"] - row["Upper left corner X"]) / width
            h = (row["Lower right corner Y"] - row["Upper left corner Y"]) / height

            yolo_line = f"{class_idx} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"

            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
            txt_file_path = os.path.join(lisa_full_labels_path, txt_file_name)

            print(txt_file_name)
            print(txt_file_path)
            with open(txt_file_path, 'a') as f:
                f.write(yolo_line + "\n")

# Generate LISA traffic lights full
def generate_lisa_traffic_lights_full():

    if(os.path.exists(lisa_full_images_path)):
        shutil.rmtree(lisa_full_images_path)
    os.makedirs(lisa_full_images_path, exist_ok = True)

    if(os.path.exists(lisa_full_labels_path)):
        shutil.rmtree(lisa_full_labels_path)
    os.makedirs(lisa_full_labels_path, exist_ok = True)

    # Generate images
    for root, dirs, files in os.walk(lisa_unzip_path):
        for file_name in files:
            if file_name.endswith(".jpg"):
                shutil.copy(os.path.join(root, file_name), lisa_full_images_path)
 

    # Generate labels
    for root, dirs, files in os.walk(lisa_annotations_base_path):
        for file_name in files:
            if file_name.endswith("frameAnnotationsBOX.csv"):
                csv_file_path = os.path.join(root, file_name)
                process_lisa_traffic_lights_annotation(csv_file_path)


    # Remove images which without labels
    for file_name in os.listdir(lisa_full_images_path):  
        image_path = os.path.join(lisa_full_images_path, file_name)
        label_path = os.path.join(lisa_full_labels_path, os.path.splitext(os.path.basename(file_name))[0] + ".txt")
        #print(image_path)
        #print(label_path)
        if not os.path.exists(label_path):
            os.remove(image_path)
            #print(image_path)


# Generate LISA traffic signs full
def generate_lisa_traffic_signs_full():

    class_mapping = {'addedLane': 0, 'curveLeft': 1, 'curveRight': 2, 'dip': 3, 'doNotEnter': 4, 
                 'doNotPass': 5, 'intersection': 6, 'keepRight': 7, 'laneEnds': 8, 'merge': 9, 
                 'noLeftTurn': 10, 'noRightTurn': 11, 'pedestrianCrossing': 12, 'rampSpeedAdvisory20': 13, 'rampSpeedAdvisory35': 14, 
                 'rampSpeedAdvisory40': 15, 'rampSpeedAdvisory45': 16, 'rampSpeedAdvisory50': 17, 'rampSpeedAdvisoryUrdbl': 18, 'rightLaneMustTurn': 19, 
                 'roundabout': 20, 'school': 21, 'schoolSpeedLimit25': 22, 'signalAhead': 23, 'slow': 24, 
                 'speedLimit15': 25, 'speedLimit25': 26, 'speedLimit30': 27, 'speedLimit35': 28, 'speedLimit40': 29, 
                 'speedLimit45': 30, 'speedLimit50': 31, 'speedLimit55': 32, 'speedLimit65': 33, 'speedLimitUrdbl': 34, 
                 'stop': 35, 'stopAhead': 36, 'thruMergeLeft': 37, 'thruMergeRight': 38, 'thruTrafficMergeLeft': 39, 
                 'truckSpeedLimit55': 40, 'turnLeft': 41, 'turnRight': 42, 'yield': 43, 'yieldAhead': 44, 
                 'zoneAhead25': 45, 'zoneAhead45': 46}

    # Generate images and labels
    annotations = pd.read_csv(lisa_annotations_base_path, delimiter=';')

    # Generate images and labels according to each row in annotation file.
    for _, row in annotations.iterrows():
        image_file_name = row["Filename"]
        class_name = row["Annotation tag"]

        # Check if class exists
        if class_name not in class_mapping:
            continue

        source_image_path = os.path.join(lisa_unzip_path + image_file_name)

        # Check if file is from aiua video which has no color. Add 'grayscale' keyword in file name
        if image_file_name.startswith('aiua'):
            desc_image_path = os.path.join(lisa_full_images_path, image_file_name.split('/')[-1].replace('avi_', 'avi_grayscale_'))
        else:
            desc_image_path = os.path.join(lisa_full_images_path, image_file_name.split('/')[-1])

        if not os.path.exists(source_image_path):
            continue

        shutil.copy(source_image_path, desc_image_path)

        with Image.open(desc_image_path) as img:
            width, height = img.size

        # Get YOLO values
        class_idx = class_mapping[class_name]
        x = (row["Upper left corner X"] + row["Lower right corner X"]) / 2.0 / width
        y = (row["Upper left corner Y"] + row["Lower right corner Y"]) / 2.0 / height
        w = (row["Lower right corner X"] - row["Upper left corner X"]) / width
        h = (row["Lower right corner Y"] - row["Upper left corner Y"]) / height

        yolo_line = f"{class_idx} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"

        if image_file_name.startswith('aiua'):
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0].replace('avi_', 'avi_grayscale_') + ".txt"
        else:
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"  
        txt_file_path = os.path.join(lisa_full_labels_path, txt_file_name)

        print(txt_file_name)
        print(txt_file_path)
        with open(txt_file_path, 'a') as f:
            f.write(yolo_line + "\n")

# Generate traffic light dataset
# LISA: keep 1/10 dayClip only images
def generate_traffic_lights_dataset():
    # List to store file_names
    filtered_files = []

    # Iterate through the files in the images folder
    for image_file_name in os.listdir(lisa_full_images_path):
        # Check if the file does not contain 'night' and 'Sequence'
        if 'night' not in image_file_name and 'Sequence' not in image_file_name:
            filtered_files.append(image_file_name)

    # Sort the filtered file_names alphabetically
    filtered_files.sort()
    print('The size of filtered_files: ' + str(len(filtered_files)))

    # Retrieve one file from every three files
    selected_files = filtered_files[::10]
    print('The size of selected_files: ' + str(len(selected_files)))

    # Copy selected files to small version of dataset and Re-classify all 7 classes to one class 'trafficLight'
    for image_file_name in selected_files:
        shutil.copy(os.path.join(lisa_full_images_path, image_file_name), os.path.join(lisa_full_images_path, image_file_name))
        txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
        dest_txt_file_path = os.path.join(dataset_labels_path, txt_file_name)
        shutil.copy(os.path.join(lisa_full_labels_path, txt_file_name), dest_txt_file_path)

        #Re-classify all 7 classes to one class 'trafficLight'
        with open(dest_txt_file_path, 'r') as file:
            lines = file.readlines()
        for i in range(len(lines)):
            if lines[i]:  # Check if the line is not empty
                lines[i] = '0' + lines[i][1:] 
        # Write the modified lines back to the file
        with open(dest_txt_file_path, 'w') as file:
            file.writelines(lines)

# Generate lisa traffic sign dataset
# LISA: find only color 'stop', 'stopAhead','yield', 'yieldAhead'; find both color and grayscale 'speedLimit' 
def generate_traffic_signs_dataset():
    # List to store file_names
    filtered_files = []

    # Iterate through the files in the images folder to find 'stop', 'stopAhead','yield', 'yieldAhead', 'speedLimit' images.   
    for image_file_name in os.listdir(lisa_full_images_path):
        if ('stop' in image_file_name and 'grayscale' not in image_file_name
            or 'yield' in image_file_name and 'grayscale' not in image_file_name 
            or 'speedLimit' in image_file_name):
            filtered_files.append(image_file_name)
    print('The size of filtered_files: ' + str(len(filtered_files)))


    # Copy filtered files to small version of dataset
    for image_file_name in filtered_files:
        shutil.copy(os.path.join(lisa_full_images_path, image_file_name), os.path.join(lisa_full_images_path, image_file_name))
        txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
        shutil.copy(os.path.join(lisa_full_labels_path, txt_file_name), os.path.join(dataset_labels_path, txt_file_name))



def zip_folder(folder_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Add file to the zip file, preserving folder structure
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))


# MAIN entry

# # generate LISA full
# if(os.path.exists(lisa_full_images_path)):
#     shutil.rmtree(lisa_full_images_path)
# os.makedirs(lisa_full_images_path, exist_ok = True)

# if(os.path.exists(lisa_full_labels_path)):
#     shutil.rmtree(lisa_full_labels_path)
# os.makedirs(lisa_full_labels_path, exist_ok = True)

# if model_name == 'traffic_lights':
#     generate_lisa_traffic_lights_full()
# if model_name == 'traffic_signs': 
#     generate_lisa_traffic_signs_full() 
# # end of generate LISA full

# generate dataset
if(os.path.exists(dataset_images_path)):
    shutil.rmtree(dataset_images_path)
os.makedirs(dataset_images_path, exist_ok = True)

if(os.path.exists(dataset_labels_path)):
    shutil.rmtree(dataset_labels_path)
os.makedirs(dataset_labels_path, exist_ok = True)

if model_name == 'traffic_lights':
    generate_traffic_lights_dataset()
    
if model_name == 'traffic_signs': 
    generate_traffic_signs_dataset()
# end of generate dataset

#zip dataset
zip_folder(dataset_base_path, arcname=dataset_zipfile_name)

#upload to Google Drive
shutil.copy2(dataset_zipfile_path, dataset_zipfile_google_drive_path)
