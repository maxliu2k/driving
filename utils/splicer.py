import cv2
import os
import shutil

def splice_images(video_path, video_name, output_folder, time_interval):
    
    # open the video file
    video = cv2.VideoCapture(video_path)
    print(video_path)
    if not video.isOpened():
        print("Error opening video file")
        return

    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # get video information
    fps = round(video.get(cv2.CAP_PROP_FPS))

    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # read the video frame by frame
    for i in range(frame_count):
        success, frame = video.read()

        if not success:
            print("Error reading frame")
            break

        # check if the current frame is within the time interval
        if i / fps % time_interval == 0:
            # save the frame
            cv2.imwrite(os.path.join(output_folder, video_name + f"_{(i//fps):04d}.jpg"), frame)

    video.release()
    print("Splicing complete")


# #if __name__ == "__main__":
# for i in range(8754, 8770):

#     # #generate images from videos
#     # video_path = f"D:/TeenSafe/Dataset/Houston_videos/videos/IMG_{i:04d}_H264.mov"
#     # video_name = f"{i:04d}"
#     # output_folder = "D:/TeenSafe/Dataset/Houston_videos/images/IMG_" + video_name + "/"
#     # time_interval = 3  # interval in seconds
#     # splice_images(video_path, video_name, output_folder, time_interval)

#     #generate images which include traffic boxes
#     video_path = f"D:/TeenSafe/Dataset/Houston_traffic_lights/videos/IMG_{i:04d}.mp4"
#     video_name = f"{i:04d}"
#     output_folder = "D:/TeenSafe/Dataset/Houston_traffic_lights/images/IMG_" + video_name + "/"
#     time_interval = 1  # interval in seconds
#     splice_images(video_path, video_name, output_folder, time_interval)


# # generate background yolov8 images
# destination_folder = "D:/TeenSafe/dataset/Houston_traffic_signs/yolov8_images_background/train/images/"
# for i in range(8754, 8770):
#     source_folder = f"D:/TeenSafe/dataset/Houston_traffic_signs/images_background/IMG_{i:04d}/"
#     if os.path.exists(source_folder):
#         for filename in os.listdir(source_folder):
#             src = os.path.join(source_folder, filename)
#             dst = os.path.join(destination_folder, filename)
#             if os.path.isfile(src):  # copy only files
#                 shutil.copy(src, dst)

# # generate background yolov8 labels
# image_folder = "D:/TeenSafe/dataset/Houston_traffic_signs/yolov8_images_background/train/images/"
# label_folder = "D:/TeenSafe/dataset/Houston_traffic_signs/yolov8_images_background/train/labels/"
# os.makedirs(label_folder, exist_ok=True)

# for filename in os.listdir(image_folder):
#     if filename.lower().endswith(".jpg"):
  
#         txt_name = filename.replace(".jpg", ".txt")
#         txt_path = os.path.join(label_folder, txt_name)

#         open(txt_path, "w").close()

#         print(f"Created {txt_path}")



# print the amount of image files 
root_folder = r"D:/TeenSafe/dataset/Houston_traffic_signs/images_traffic_signs"

# Loop through each subfolder inside root_folder
for subfolder in os.listdir(root_folder):
    subfolder_path = os.path.join(root_folder, subfolder)

    # Only process directories
    if os.path.isdir(subfolder_path):
        file_count = len([
            f for f in os.listdir(subfolder_path)
            if os.path.isfile(os.path.join(subfolder_path, f))
        ])

        print(f"{subfolder}: {file_count} files")