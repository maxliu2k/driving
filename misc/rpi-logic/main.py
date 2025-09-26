import cv2 as cv

def main():
    # get the available camera devices
    camera_devices = []

    for i in range(2):
        cap = cv.VideoCapture(i)
        if cap.isOpened():
            camera_devices.append(i)
        cap.release()

    # primary camera is for analyzing the road
    road_camera = cv.VideoCapture(camera_devices[0])

    # secondary camera is for analyzing the driver
    driver_camera = cv.VideoCapture(camera_devices[1])

    # load the accelerometer sensor

if __name__ == "__main__":
    main()