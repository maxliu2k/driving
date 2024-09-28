import cv2
import os

def splice_images(video_path, video_name, output_folder, time_interval):
    # open the video file
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        cv2.VideoCapture(video_path[0:16] + ".mov")

    if not video.isOpened():
        print("Error opening video file")
        return

    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    image_path = output_folder + "/" + video_name
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    
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
            cv2.imwrite(os.path.join(image_path, video_name + "_" + f"{(i//fps):04d}.jpg"), frame)

    video.release()
    print("Splicing complete:" + (str) (i//fps))


if __name__ == "__main__":
    for i in range(1409, 1446):
        video_path = f"videos/IMG_{i:04d}.MOV"
        video_name = f"{i:04d}"
        output_folder = "images"
        time_interval = 1  # interval in seconds
        splice_images(video_path, video_name, output_folder, time_interval)