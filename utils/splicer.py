import cv2
import os

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


#if __name__ == "__main__":
for i in range(8754, 8770):
    video_path = f"C:/TeenSafe_backup/Dataset/Houston_traffic_signs_original/videos/IMG_{i:04d}.mp4"
    video_name = f"{i:04d}"
    output_folder = "C:/TeenSafe_backup/Dataset/Houston_traffic_signs_original/images/IMG_" + video_name + "/"
    time_interval = 1  # interval in seconds
    splice_images(video_path, video_name, output_folder, time_interval)