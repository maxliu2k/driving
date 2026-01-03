import os
import shutil
import pandas as pd
from PIL import Image
import zipfile
import random
import cv2
import numpy as np


# pass in model name
model_name='traffic_signs' #{'traffic_lights', 'traffic_signs', 'traffic_bulbs'}
model_type='Houston' #{'LISA_Houston', 'LISA', 'Houston'}
model_per_bg_images=3
is_unified_speed_limit = True
does_generate_LISA_yolov8 = False
# end of pass in

lisa_unzip_path='D:/TeenSafe/DataSet/LISA_'+ model_name + '_original/'
lisa_full_images_path ='D:/TeenSafe/DataSet/LISA_'+ model_name + '_yolov8/images/'
lisa_full_labels_path ='D:/TeenSafe/DataSet/LISA_'+ model_name + '_yolov8/labels/'

houston_full_images_path ='D:/TeenSafe/DataSet/Houston_'+ model_name + '/yolov8_images_' + model_name + '/train/images/'
houston_full_labels_path ='D:/TeenSafe/DataSet/Houston_'+ model_name + '/yolov8_images_' + model_name + '/train/labels/'
houston_full_bg_images_path ='D:/TeenSafe/DataSet/Houston_'+ model_name + '/yolov8_images_background/train/images/'
houston_full_bg_labels_path ='D:/TeenSafe/DataSet/Houston_'+ model_name + '/yolov8_images_background/train/labels/'

dataset_base_path ='D:/TeenSafe/DataSet/' + model_name + '_dataset/'

dataset_train_images_path = dataset_base_path + 'train/images/'
dataset_train_labels_path = dataset_base_path + 'train/labels/'

dataset_valid_images_path = dataset_base_path + 'valid/images/'
dataset_valid_labels_path = dataset_base_path + 'valid/labels/'

dataset_test_images_path = dataset_base_path + 'test/images/'
dataset_test_labels_path = dataset_base_path + 'test/labels/'

temp_dataset_base_path = dataset_base_path +'temp/'
temp_dataset_images_path = temp_dataset_base_path + 'images/'
temp_dataset_labels_path = temp_dataset_base_path + 'labels/'
dataset_zipfile_name = dataset_base_path.split('/')[-2] + '.zip'
dataset_zipfile_path = 'D:/TeenSafe/DataSet/' + dataset_zipfile_name
dataset_zipfile_google_drive_path = 'G:/My Drive/Colab Notebooks/' + model_name + '/' + dataset_zipfile_name


###############################################################################
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

            with open(txt_file_path, 'a') as f:
                f.write(yolo_line + "\n")

# Generate LISA traffic lights yolov8
def generate_lisa_traffic_lights_yolov8():

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
    for root, dirs, files in os.walk(lisa_unzip_path+ 'Annotations/'):
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

# Generate traffic light dataset
def generate_traffic_lights_dataset():

    class_mapping = {'trafficLight': 0}
    
    # begin of LISA: keep 1/10 dayClip only images; keep 1/20 dayClip when mix with Houston
    if 'LISA' in model_type:
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
        if 'Houston' in model_type:
            selected_files = filtered_files[::20]
        else:
            selected_files = filtered_files[::10]
        print('The size of LISA selected_files: ' + str(len(selected_files)))

        # Copy selected files to small version of dataset and Re-classify all 7 classes to one class 'trafficLight'
        for image_file_name in selected_files:
            shutil.copy(os.path.join(lisa_full_images_path, image_file_name), os.path.join(dataset_train_images_path, image_file_name))
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
            dest_txt_file_path = os.path.join(dataset_train_labels_path, txt_file_name)
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

    # end of LISA

    # begin of Houston
    if 'Houston' in model_type:
        # copy no-background images
        for image_file_name in os.listdir(houston_full_images_path):
            #print(os.path.join(houston_full_images_path, image_file_name))
            shutil.copy(os.path.join(houston_full_images_path, image_file_name), os.path.join(dataset_train_images_path, image_file_name))
            
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
            dest_txt_file_path = os.path.join(dataset_train_labels_path, txt_file_name)
            #print(dest_txt_file_path)
            shutil.copy(os.path.join(houston_full_labels_path, txt_file_name), dest_txt_file_path)

        # copy background images
        for idx, image_file_name in enumerate(os.listdir(houston_full_bg_images_path)):
            if idx % model_per_bg_images != 0:
                continue
            #print(os.path.join(houston_full_images_path, image_file_name))
            shutil.copy(os.path.join(houston_full_bg_images_path, image_file_name), os.path.join(dataset_train_images_path, image_file_name))
            
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
            dest_txt_file_path = os.path.join(dataset_train_labels_path, txt_file_name)
            #print(dest_txt_file_path)
            shutil.copy(os.path.join(houston_full_bg_labels_path, txt_file_name), dest_txt_file_path)

    # end of Houston 

# Generate LISA traffic signs yolov8
def generate_lisa_traffic_signs_yolov8():

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
    annotations = pd.read_csv(lisa_unzip_path+ 'allAnnotations.csv', delimiter=';')

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

# Generate traffic sign dataset 
def generate_traffic_signs_dataset():

    #note: can be different classes from roboflow
    class_mapping=None
    if is_unified_speed_limit == False:
        class_mapping = {
                    'stop': 0, 'stopAhead': 1, 'yield': 2, 'yieldAhead': 3,
                    'schoolSpeedLimit20': 4, 'schoolSpeedLimit25': 5, 
                    'speedLimit15': 6, 'speedLimit20': 7, 'speedLimit25': 8, 'speedLimit30': 9, 
                    'speedLimit35': 10, 'speedLimit40': 11, 'speedLimit45': 12, 'speedLimit50': 13, 
                    'speedLimit55': 14, 'speedLimit60': 15, 'speedLimit65': 16, 'speedLimit70': 17}
    
    if is_unified_speed_limit == True:
        class_mapping = {
                    'stop': 0, 'stopAhead': 1, 'yield': 2, 'yieldAhead': 3,
                    'speedLimit':4}

    
    # begin of LISA: find only color 'stop', 'stopAhead','yield', 'yieldAhead', 'speedLimit' 
    if 'LISA' in model_type:
    # Generate images and labels
        annotations = pd.read_csv(lisa_unzip_path+ 'allAnnotations.csv', delimiter=';')

        # Generate images and labels according to each row in annotation file.
        temp_traffic_signs_list = []
        for _, row in annotations.iterrows():
            image_file_name = row["Filename"]
            class_name = row["Annotation tag"]


            # exclude aiua to only include color image and also check if class exists
            if image_file_name.startswith('aiua') or class_name not in class_mapping:
                continue

            source_image_path = os.path.join(lisa_unzip_path + image_file_name) 
            temp_desc_image_path = os.path.join(temp_dataset_images_path, image_file_name.split('/')[-1])   
            if not os.path.exists(source_image_path):
                continue   

            shutil.copy(source_image_path, temp_desc_image_path)

            with Image.open(temp_desc_image_path) as img:
                width, height = img.size

            # Get YOLO values
            class_idx = class_mapping[class_name]
            x = (row["Upper left corner X"] + row["Lower right corner X"]) / 2.0 / width
            y = (row["Upper left corner Y"] + row["Lower right corner Y"]) / 2.0 / height
            w = (row["Lower right corner X"] - row["Upper left corner X"]) / width
            h = (row["Lower right corner Y"] - row["Upper left corner Y"]) / height

            yolo_line = f"{class_idx} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"

            
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"  
            txt_file_path = os.path.join(temp_dataset_labels_path, txt_file_name)

            with open(txt_file_path, 'a') as f:
                f.write(yolo_line + "\n")
            
            
            temp_traffic_signs_list.append(image_file_name.split('/')[-1] + '_' + class_name)

        random.shuffle(temp_traffic_signs_list)  
        filtered_list = []
        for class_name in class_mapping.keys(): 

            # if (class_name=='schoolSpeedLimit20'
            #     or class_name == 'speedLimit30' 
            #     or class_name == 'speedLimit35' 
            #     or class_name == 'speedLimit40' 
            #     or class_name == 'speedLimit45'
            #     or class_name == 'speedLimit50'):
            #     continue

            if ('speedlimit' in class_name.lower()):
                continue

            #print(class_name)
            count=0
            for item in temp_traffic_signs_list:
                if item.endswith(class_name):
                    filtered_list.append(item.replace('_'+ class_name, ''))
                    count = count + 1
                if ('stop'in class_name or 'yield' in class_name):
                    if count==100:
                        break   
                    
            print('LISA ' + class_name + ':' + str(count))

        for item in filtered_list:
            temp_source_image_path = os.path.join(temp_dataset_images_path, item) 
            desc_image_path = os.path.join(dataset_train_images_path, item.replace('.png', '.jpg'))   
            #shutil.copy(temp_source_image_path, desc_image_path)
            with Image.open(temp_source_image_path) as img:
                # Convert the image to RGB (JPEG doesn't support transparency)
                rgb_img = img.convert('RGB')
                # Save the image in JPG format
                rgb_img.save(desc_image_path, quality=95)

            temp_source_label_path = os.path.join(temp_dataset_labels_path, item.replace('.png', '.txt')) 
            desc_label_path = os.path.join(dataset_train_labels_path, item.replace('.png', '.txt'))   
            shutil.copy(temp_source_label_path, desc_label_path)

            
            #note: Re-mapping - unified speed limit   
            if is_unified_speed_limit == True:
                with open(desc_label_path, 'r') as file:
                    lines = file.readlines()
                for i in range(len(lines)):
                    if lines[i]:  # Check if the line is not empty
                        if int(lines[i].split(' ')[0])>=4:
                            lines[i] = str(class_mapping['speedLimit']) + ' ' + ' '.join(lines[i].split(' ')[1:])   

            # Write the modified lines back to the file
            with open(desc_label_path, 'w') as file:
                file.writelines(lines)

        # end of LISA

    # begin of Houston
    if 'Houston' in model_type:

        # copy no-background images
        houston_class_count = {key: 0 for key in class_mapping.keys()}
        for image_file_name in os.listdir(houston_full_images_path):
            #print(os.path.join(houston_full_images_path, image_file_name))
            shutil.copy(os.path.join(houston_full_images_path, image_file_name), os.path.join(dataset_train_images_path, image_file_name))
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
            txt_file_path = os.path.join(houston_full_labels_path, txt_file_name)
            dest_txt_file_path = os.path.join(dataset_train_labels_path, txt_file_name)
            shutil.copy(txt_file_path, dest_txt_file_path)
            #print(txt_file_path)
            #print(dest_txt_file_path)
  
            #note: Re-mapping roboflow class to class_mapping defined here - individual speed limit
            if is_unified_speed_limit == False:               
                with open(dest_txt_file_path, 'r') as file:
                    lines = file.readlines()
                for i in range(len(lines)):
                    if lines[i]:  # Check if the line is not empty
                        if lines[i].split(' ')[0]=='0':             
                            lines[i] = str(class_mapping['schoolSpeedLimit20']) + ' ' + ' '.join(lines[i].split(' ')[1:])   
                            houston_class_count['schoolSpeedLimit20'] += 1              
                        if lines[i].split(' ')[0]=='1':
                            lines[i] = str(class_mapping['speedLimit30']) + ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['speedLimit30'] += 1          
                        if lines[i].split(' ')[0]=='2':
                            lines[i] = str(class_mapping['speedLimit35'])+ ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['speedLimit35'] += 1 
                        if lines[i].split(' ')[0]=='3':
                            lines[i] = str(class_mapping['speedLimit40'])+ ' ' + ' '.join(lines[i].split(' ')[1:])
                            houston_class_count['speedLimit40'] += 1  
                        if lines[i].split(' ')[0]=='4':
                            lines[i] = str(class_mapping['speedLimit45'])+ ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['speedLimit45'] += 1  
                        if lines[i].split(' ')[0]=='5':
                            lines[i] = str(class_mapping['speedLimit50'])+ ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['speedLimit50'] += 1  
                        if lines[i].split(' ')[0]=='6':
                            lines[i] = str(class_mapping['stop']) + ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['stop'] += 1 
                        if lines[i].split(' ')[0]=='7':
                            lines[i] = str(class_mapping['stopAhead']) + ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['stopAhead'] += 1
                        if lines[i].split(' ')[0]=='8':
                            lines[i] = str(class_mapping['yield']) + ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['yield'] += 1 

            #note: Re-mapping roboflow class to class_mapping defined here - unified speed limit
            if is_unified_speed_limit == True:
                with open(dest_txt_file_path, 'r') as file:
                    lines = file.readlines()
                for i in range(len(lines)):
                    if lines[i]:  # Check if the line is not empty
                        if lines[i].split(' ')[0] in {'0', '1', '2','3','4','5'}:
                            lines[i] = str(class_mapping['speedLimit']) + ' ' + ' '.join(lines[i].split(' ')[1:])   
                            houston_class_count['speedLimit'] += 1 
                        if lines[i].split(' ')[0]=='6':
                            lines[i] = str(class_mapping['stop']) + ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['stop'] += 1 
                        if lines[i].split(' ')[0]=='7':
                            lines[i] = str(class_mapping['stopAhead']) + ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['stopAhead'] += 1
                        if lines[i].split(' ')[0]=='8':
                            lines[i] = str(class_mapping['yield']) + ' ' + ' '.join(lines[i].split(' ')[1:]) 
                            houston_class_count['yield'] += 1

            # Write the modified lines back to the file
            with open(dest_txt_file_path, 'w') as file:
                file.writelines(lines)

        for key, value in houston_class_count.items():
            if value!=0:
                print(f'Houston {key}: {value}')


        # copy background images
        for idx, image_file_name in enumerate(os.listdir(houston_full_bg_images_path)):
            if idx % model_per_bg_images != 0:
                continue
            #print(os.path.join(houston_full_images_path, image_file_name))
            shutil.copy(os.path.join(houston_full_bg_images_path, image_file_name), os.path.join(dataset_train_images_path, image_file_name))
            
            txt_file_name = os.path.splitext(os.path.basename(image_file_name))[0] + ".txt"
            dest_txt_file_path = os.path.join(dataset_train_labels_path, txt_file_name)
            #print(dest_txt_file_path)
            shutil.copy(os.path.join(houston_full_bg_labels_path, txt_file_name), dest_txt_file_path)

    # end of Houston 

    # choose data.yaml
    if is_unified_speed_limit == False:
        shutil.copy(os.path.join(dataset_base_path, 'data_individual_speed_limit.yaml'), os.path.join(dataset_base_path, 'data.yaml'))
    if is_unified_speed_limit == True:
        shutil.copy(os.path.join(dataset_base_path, 'data_unified_speed_limit.yaml'), os.path.join(dataset_base_path, 'data.yaml'))

#########################################################################################################
# Augmentation
def adjust_brightness_contrast(img, brightness=0, contrast=0):
    img = img.astype(np.float32)
    if contrast != 0:
        factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
        img = factor * (img - 128) + 128
    img += brightness
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def adjust_saturation(img, factor=1.2):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] *= factor
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def augment_image(img):
    # Random brightness and contrast
    brightness = random.randint(-30, 30)
    contrast = random.randint(-30, 30)
    img_aug = adjust_brightness_contrast(img, brightness, contrast)

    # Random saturation
    saturation_factor = random.uniform(0.7, 1.3)
    img_aug = adjust_saturation(img_aug, saturation_factor)

    return img_aug

def generate_augment_dataset (image_folder, label_folder):
    for file_full_name in os.listdir(image_folder):   
        image_path = os.path.join(image_folder, file_full_name)
        file_name, ext = os.path.splitext(file_full_name)
        label_path = os.path.join(label_folder, f"{file_name}.txt")
        #print(f'{image_path}')
        #print(f'{label_path}')

        img = cv2.imread(image_path)
        # Generate 2 augmented images
        for i in range(2):
            img_aug = augment_image(img)    
            img_aug_path = os.path.join(image_folder, f"{file_name}_aug{i+1}{ext}")
            label_aug_path = os.path.join(label_folder, f"{file_name}_aug{i+1}.txt")
            #print(f'{img_aug_path}')
            #print(f'{label_aug_path}')
            cv2.imwrite(img_aug_path, img_aug)
            shutil.copy(label_path, label_aug_path)
            #cv2.imwrite(img_aug_path, img_aug, [int(cv2.IMWRITE_JPEG_QUALITY), 75])

########################################################################################################
def zip_folder(folder_path, zip_file_path):
    #print(folder_path)
    #print(zip_file_path)
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                #print(file_path)
                # Add file to the zip file, preserving folder structure
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
########################################################################################################             

# generate LISA yolov8 (only once)
# if does_generate_LISA_yolov8 == True:
#     print ('generate LISA yolov8 full begin.')
#     if(os.path.exists(lisa_full_images_path)):
#         shutil.rmtree(lisa_full_images_path)
#     os.makedirs(lisa_full_images_path, exist_ok = True)

#     if(os.path.exists(lisa_full_labels_path)):
#         shutil.rmtree(lisa_full_labels_path)
#     os.makedirs(lisa_full_labels_path, exist_ok = True)

#     if model_name == 'traffic_lights':
#         generate_lisa_traffic_lights_yolov8()
#     if model_name == 'traffic_signs': 
#         generate_lisa_traffic_signs_yolov8() 


# generate traffic_lights and traffic_signs dataset
if model_name == 'traffic_lights' or model_name == 'traffic_signs': 
    if(os.path.exists(dataset_train_images_path)):
        shutil.rmtree(dataset_train_images_path)
    os.makedirs(dataset_train_images_path, exist_ok = True)
    if(os.path.exists(dataset_train_labels_path)):
        shutil.rmtree(dataset_train_labels_path)
    os.makedirs(dataset_train_labels_path, exist_ok = True)

    if(os.path.exists(dataset_valid_images_path)):
        shutil.rmtree(dataset_valid_images_path)
    os.makedirs(dataset_valid_images_path, exist_ok = True)
    if(os.path.exists(dataset_valid_labels_path)):
        shutil.rmtree(dataset_valid_labels_path)
    os.makedirs(dataset_valid_labels_path, exist_ok = True)

    if(os.path.exists(dataset_test_images_path)):
        shutil.rmtree(dataset_test_images_path)
    os.makedirs(dataset_test_images_path, exist_ok = True)
    if(os.path.exists(dataset_test_labels_path)):
        shutil.rmtree(dataset_test_labels_path)
    os.makedirs(dataset_test_labels_path, exist_ok = True)

    if(os.path.exists(temp_dataset_base_path)):
        shutil.rmtree(temp_dataset_base_path)
    os.makedirs(temp_dataset_base_path, exist_ok = True)

    if(os.path.exists(temp_dataset_images_path)):
        shutil.rmtree(temp_dataset_images_path)
    os.makedirs(temp_dataset_images_path, exist_ok = True)

    if(os.path.exists(temp_dataset_labels_path)):
        shutil.rmtree(temp_dataset_labels_path)
    os.makedirs(temp_dataset_labels_path, exist_ok = True)

    if model_name == 'traffic_lights':
        print('generate traffic lights dataset begin')
        generate_traffic_lights_dataset()
        for filename in os.listdir(dataset_train_images_path):
            if filename.startswith(("8759", "dayClip5")):  
                src = os.path.join(dataset_train_images_path, filename)
                dst = os.path.join(dataset_valid_images_path, filename)
                shutil.move(src, dst)
        for filename in os.listdir(dataset_train_labels_path):
            if filename.startswith(("8759", "dayClip5")):  
                src = os.path.join(dataset_train_labels_path, filename)
                dst = os.path.join(dataset_valid_labels_path, filename)
                shutil.move(src, dst)
        for filename in os.listdir(dataset_train_images_path):
            if filename.startswith(("8760", "8762", "dayClip8")):  
                src = os.path.join(dataset_train_images_path, filename)
                dst = os.path.join(dataset_test_images_path, filename)
                shutil.move(src, dst)
        for filename in os.listdir(dataset_train_labels_path):
            if filename.startswith(("8760", "8762", "dayClip8")):  
                src = os.path.join(dataset_train_labels_path, filename)
                dst = os.path.join(dataset_test_labels_path, filename)
                shutil.move(src, dst)
    if model_name == 'traffic_signs': 
        print('generate traffic signs dataset begin')
        generate_traffic_signs_dataset()
        for filename in os.listdir(dataset_train_images_path):
            if filename.startswith(("8756", "8763", "8764", "8765", "8767")):  
                src = os.path.join(dataset_train_images_path, filename)
                dst = os.path.join(dataset_valid_images_path, filename)
                shutil.move(src, dst)
        for filename in os.listdir(dataset_train_labels_path):
            if filename.startswith(("8756", "8763", "8764", "8765", "8767")):  
                src = os.path.join(dataset_train_labels_path, filename)
                dst = os.path.join(dataset_valid_labels_path, filename)
                shutil.move(src, dst)
        # for filename in os.listdir(dataset_train_images_path):
        #     if filename.startswith(("8760")):  
        #         src = os.path.join(dataset_train_images_path, filename)
        #         dst = os.path.join(dataset_test_images_path, filename)
        #         shutil.move(src, dst)
        # for filename in os.listdir(dataset_train_labels_path):
        #     if filename.startswith(("8760")):  
        #         src = os.path.join(dataset_train_labels_path, filename)
        #         dst = os.path.join(dataset_test_labels_path, filename)
        #         shutil.move(src, dst)

    if(os.path.exists(temp_dataset_base_path)):
        shutil.rmtree(temp_dataset_base_path)

# # generate traffic_lights, traffic_signs and traffic_bulbs dataset with augment
# generate_augment_dataset(dataset_train_images_path, dataset_train_labels_path)


#zip dataset
zip_folder(dataset_base_path, dataset_zipfile_path)


#upload to Google Drive
shutil.copy2(dataset_zipfile_path, dataset_zipfile_google_drive_path)



# ######################
# augmentation sample code from Chatgpt
# ######################
# #saturation
# import cv2
# import numpy as np

# def change_saturation(img, factor=1.2):
#     """
#     Change image saturation.
    
#     factor > 1.0 -> more saturated
#     factor < 1.0 -> less saturated
#     """
#     # Convert BGR to HSV
#     hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)

#     # Scale the S channel
#     hsv[:, :, 1] *= factor

#     # Clip to [0, 255]
#     hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)

#     # Convert back to BGR
#     result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
#     return result

# # Example usage
# img = cv2.imread("input.jpg")
# img_more_saturated = change_saturation(img, factor=1.5)
# img_less_saturated = change_saturation(img, factor=0.7)

# cv2.imwrite("output_more_saturated.jpg", img_more_saturated)
# cv2.imwrite("output_less_saturated.jpg", img_less_saturated)

# #################################
# #brightness
# import cv2
# import numpy as np

# def change_brightness(img, factor=1.2):
#     """
#     Change image brightness.
    
#     factor > 1.0 -> brighter
#     factor < 1.0 -> darker
#     """
#     # Convert to float to prevent overflow
#     img_float = img.astype(np.float32)

#     # Multiply pixel values by factor
#     img_bright = img_float * factor

#     # Clip to valid range 0-255 and convert back to uint8
#     img_bright = np.clip(img_bright, 0, 255).astype(np.uint8)
    
#     return img_bright

# # Example usage
# img = cv2.imread("input.jpg")
# img_brighter = change_brightness(img, factor=1.3)  # 30% brighter
# img_darker = change_brightness(img, factor=0.7)    # 30% darker

# cv2.imwrite("output_brighter.jpg", img_brighter)
# cv2.imwrite("output_darker.jpg", img_darker)


# #############
# #exposure
# import cv2
# import numpy as np

# def change_exposure(img, factor=1.2):
#     """
#     Change image exposure.
#     factor > 1.0 → brighter (overexposed)
#     factor < 1.0 → darker (underexposed)
#     """
#     # Convert image to float32 for safe multiplication
#     img_float = img.astype(np.float32)

#     # Multiply by factor
#     img_exposed = img_float * factor

#     # Clip to valid range 0-255 and convert back to uint8
#     img_exposed = np.clip(img_exposed, 0, 255).astype(np.uint8)

#     return img_exposed

# # Example usage
# img = cv2.imread("input.jpg")
# img_brighter = change_exposure(img, factor=1.3)  # brighter
# img_darker = change_exposure(img, factor=0.7)    # darker

# cv2.imwrite("output_brighter.jpg", img_brighter)
# cv2.imwrite("output_darker.jpg", img_darker)

# #############
# #guassian blur
# import cv2

# # Read image
# img = cv2.imread("input.jpg")

# # Apply Gaussian Blur (kernel size must be odd numbers)
# blurred = cv2.GaussianBlur(img, (7, 7), sigmaX=0)

# # Save result
# cv2.imwrite("output_gaussian.jpg", blurred)









