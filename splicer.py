import cv2
import os

def splice_images(video_path, output_folder, time_interval):
    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # open the video file
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        print("Error opening video file")
        return
    
    # get video information
    fps = round(video.get(cv2.CAP_PROP_FPS))
    print(fps)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    print()

    # read the video frame by frame
    for i in range(frame_count):
        success, frame = video.read()

        if not success:
            print("Error reading frame")
            break

        # check if the current frame is within the time interval
        if i / fps % time_interval == 0:
            # save the frame
            cv2.imwrite(os.path.join(output_folder, f"{i}.jpg"), frame)

    video.release()
    print("Splicing complete")


if __name__ == "__main__":
    for i in range(9, 20):
        video_path = f"Dataset20240927Videos/IMG_14{i:02d}.MOV"
        output_folder = "Dataset20240927Images"
        time_interval = 1  # interval in seconds
        splice_images(video_path, output_folder, time_interval)