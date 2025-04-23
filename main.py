from voice import Voice
import cv2
from ultralytics import YOLO
from utils import *
import smbus
from time import sleep
import math

# =============================== 
# Accelerometer (MPU6050) Setup
# ===============================
# MPU6050 Registers
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

bus = smbus.SMBus(1)     # For Raspberry Pi
Device_Address = 0x68    # MPU6050 device address

# Offsets provided for calibration
Ax_offset = 0.05
Ay_offset = -0.01
Az_offset = -1.11
Gx_offset = 0.29
Gy_offset = 0.07
Gz_offset = 0.09

def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value = value - 65536
    return value

def get_motion_data():
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)
    
    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0
    Gx = gyro_x / 131.0
    Gy = gyro_y / 131.0
    Gz = gyro_z / 131.0
    
    return Ax, Ay, Az, Gx, Gy, Gz

def get_direction_and_acceleration():
    Ax, Ay, Az, Gx, Gy, Gz = get_motion_data()
    accel_magnitude = math.sqrt(Ax**2 + Ay**2 + Az**2)
    
    # Simple directional estimation using Ax and Ay
    if Ax > 0.5:
        direction = "Right"
    elif Ax < -0.5:
        direction = "Left"
    elif Ay > 0.5:
        direction = "Forward"
    elif Ay < -0.5:
        direction = "Backward"
    else:
        direction = "Stationary"
    
    return direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz

# ========================================
# Update Lights Collection Function
# ========================================
def update_lights(new_light_data, old_light_data):
    """
    new_light_data: list of tuples containing (x1, y1, x2, y2, color, light_conf, color_conf, changed)
    lights_collection: list to store the light data [light_data, light_data, ...]
    """

    new_lights_to_add = [True for _ in range(len(new_light_data))]
                      # [action for object in container if condition] 

    # check if the center of the light is within the bounds of any of the current lights in the list
    for old_light in old_light_data:

        center_x = (old_light[0] + old_light[2]) / 2
        center_y = (old_light[1] + old_light[3]) / 2

        # for light in lights_collection: 
        #     light[7] = -1

        should_remove = True
        for idx, new_light in enumerate(new_light_data):
            if new_light[0] <= center_x <= new_light[2] and new_light[1] <= center_y <= new_light[3]:
                should_remove = False
                new_lights_to_add[idx] = False
                # Update existing light
                new_light_color = new_light[4]

                old_light_data[idx] = new_light

                # Check if current color is different from the old color
                if old_light[4] != new_light_color:
                    old_light_data[idx][7] = True  # Mark as changed

        if should_remove:
            old_light_data.remove(old_light)      
      
    # Add new lights that are not already in the old lights
    for idx, add in enumerate(new_lights_to_add):
        if add:
            old_light_data.append(new_light_data[idx])
        
    return old_light_data

# ========================================
# Main function integrating vision and IMU
# ========================================
def main():
    voice = Voice("piper.onnx")
    count = 0
    # Load YOLO model
    l_model = YOLO('bestlights.pt')
    # s_model = YOLO('bestsigns.pt') 
    b_model = YOLO('bestbulbs.pt')

    # Start video stream
    # cap = cv2.VideoCapture(0)

    # alternatively, use a video file 
    cap = cv2.VideoCapture('videoTest/IMG_1409.MOV')

    voice.speak("Recording started!")

    # (x1,y1,x2,y2,color,light_conf,color_conf) 
    left_turn_signals = [(0.2,0.2,0.4,0.4,'green',0.9,0.9)] # Example data
    right_turn_signals = [(0.5,0.5,0.7,0.7,'red',0.9,0.9)] # Example data
    forward_signals = [(0.8,0.8,1.0,1.0,'yellow',0.9,0.9)] # Example data

    red = False

    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break

        # ---------------------------------
        # Get accelerometer data
        # ---------------------------------
        direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz = get_direction_and_acceleration()
        print(f"Accel -> Direction: {direction}, Accel: {accel_magnitude:.2f}, "
              f"Ax: {(Ax+Ax_offset):.2f}, Ay: {(Ay+Ay_offset):.2f}, Az: {(Az+Az_offset):.2f}")
        
        # identify traffic signs in the image
        # s_results = s_model(frame) 

        # ---------------------------------
        # Traffic Lights Detection via YOLO
        # ---------------------------------
        l_results = l_model(frame)  # Detect traffic lights
        annotated_frame = l_results[0].plot()
        identified_lights = []

        for result in l_results[0].boxes:
            # check confidence
            if result.conf > 0.5:
                print(result)

                # extract the bounding box coordinates
                x, y, w, h = result.xywh[0]
                # print("IMAGE COORDINATES")
                # print(x, y, w, h)


                # crop the image to the traffic light
                cropped_frame = crop_image(frame, (x, y, w, h))

                # for debugging, save the cropped image as a file
                # cv2.imwrite("cropped.jpg", cropped_frame) 

                # also save the original frame annotated with the bounding box
                # cv2.imwrite("annotated.jpg", annotated_frame)

                # identify the bulb color in the image
                b_results = b_model(cropped_frame)
                # print(b_results)

                # format the data for the update_lights function
                x1, y1, x2, y2 = result.xyxy[0]
                color = b_results[0].names[0]
                light_conf = result.conf
                color_conf = b_results[0].boxes
                identified_lights.append((x1, y1, x2, y2, color, light_conf, color_conf, False))
                print(color)
                print(color_conf)
        
        # Update the lights collection with new detections
        # lights_collection = update_lights(identified_lights, lights_collection) 
        # print(f"Updated Lights Collection: {lights_collection}") 
        lights_collection = identified_lights
        
        # ---------------------------------
        # Trigger Voice Feedback Based on Analysis
        # ---------------------------------
        if (count % 5 == 0):
            temp = red
            for idx, light in enumerate(lights_collection):
                # if light[7] and light[4].lower() == 'green' and direction == "Stationary":
                    # voice.speak("Green")
                    # # Reset the changed flag after speaking
                    # updated = list(light)
                    # updated[7] = False
                    # lights_collection[idx] = tuple(updated)
                if (light[4].lower() == "stop" or light[4].lower() == "STOP"):
                    red = True
            if (red and not temp):
                voice.speak("red light detected")
            elif (red and temp):
                voice.speak("red light still detected")
            elif (not red and temp):
                voice.speak("red light no longer detected")
            
            # Example: if moving forward with high acceleration (indicating speeding), warn to slow down
            # if direction == "Forward" and accel_magnitude > 1.5:
            #     voice.speak("Slow down!")

            # # identify the speed limit in the image

            # # React to the analysis

            # # TTS for the lights
            # # - If stopped at right light that turns green, say "Green"
            # if False:
            #     voice.speak('Green') 
            
            # # simulate the AI finding two new lights
            # new_lights = [(0.1,0.1,0.3,0.3,'green',0.9,0.9, False), (0.4,0.4,0.6,0.6,'red',0.9,0.9, False)]

            # # TTS for the speed limit
            # # - If car exceeds speed limit, say "Slow down!"


            # ---------------------------------
            # Display the annotated frame
            # ---------------------------------
            cv2.imshow("Annotated Frame", annotated_frame)
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        sleep(0.1)  # Small delay to ease CPU load

        

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()