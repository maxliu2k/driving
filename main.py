# Voting System between frames to improve accuracy
# 1. Red light detection Example: if, in the last 3 frames, the red light was detected more than 50% of the time, then consider it as detected.

from voice import Voice
import cv2
from ultralytics import YOLO
from utils import *
#import smbus
from time import sleep
import math
import threading
import pytesseract
import re
import serial
import adafruit_gps
import time
from collections import deque
import queue
# import pynmea2 #pip install pyserial pynmea2

voice_queue = queue.Queue()

def speak_async(voice, text):
    threading.Thread(target=voice.speak, args=(text,), daemon=True).start()

def speak_queued(text):
    voice_queue.put(text)

# ===== GPS Setup =====

uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=30)

gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

gps.send_command(b'PMTK220,1000')

last_print = time.monotonic()



# =============================== 
# Accelerometer (MPU6050) Setup
# ===============================
# Accelerometer Registers
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

# For Raspberry Pi
bus = smbus.SMBus(1)     

# MPU6050 device address
Device_Address = 0x68

# Offsets provided for calibration
Ax_offset = 0.05
Ay_offset = -0.01
Az_offset = -1.11
Gx_offset = 0.29
Gy_offset = 0.07
Gz_offset = 0.09

# Filtering and Thresholds
GYRO_WINDOW = 10
GYRO_THRESHOLD = 5.0 # degrees/sec

# Deques for storing gyro data
gyro_buffer = deque(maxlen=GYRO_WINDOW)

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

def detect_turn():
    """
    Design Notes:
    - sometimes the road can have bumps so we might need a filter
    - primarily rely on gyro (yaw rate) to detect turns
        - either y or z axis, tbd
    """
    _, _, _, Gx, Gy, Gz = get_motion_data()
    gyro_buffer.append(Gy)

    # Compute moving average
    gyro_avg = sum(gyro_buffer) / len(gyro_buffer)

    # Determine the turn:
    if abs(gyro_avg) > GYRO_THRESHOLD:
        if gyro_avg > 0:
            return "Right Turn"
        else:
            return "Left Turn"
    else:
        return "Straight"


# def read_gps_speed(serial_port='/dev/serial0', baudrate=9600):
#     # Open serial connection to GPS
#     speed_mph = 0
#     with serial.Serial(serial_port, baudrate, timeout=1) as ser:
#         while True:
#             try:
#                 line = ser.readline().decode('ascii', errors='replace')
#                 if line.startswith('$GPRMC'):
#                     msg = pynmea2.parse(line)
#                     if msg.status == 'A':  # A = valid, V = invalid
#                         speed_knots = float(msg.spd_over_grnd)
#                         speed_mph = speed_knots * 1.15078
#             except pynmea2.ParseError:
#                 continue
#     return speed_mph

def detect_best_box(class_names, boxes, box_name, match_mode, conf, is_print):
    
    detected_boxes=[]
    if match_mode == "equal":
        detected_boxes = [
            box for box in boxes
            if class_names[int(box.cls[0].item())].lower()==box_name.lower() and box.conf[0].item() > conf]
    if match_mode == "contain":
        detected_boxes = [
            box for box in boxes
            if box_name.lower() in class_names[int(box.cls[0].item())].lower() and box.conf[0].item() > conf]

    # If any such boxes exist, get the one with the highest confidence
    if detected_boxes:
        best_detected_box = max(detected_boxes, key=lambda b: b.conf[0].item())
        
        # Extract details
        best_detected_box_id = int(best_detected_box.cls[0].item())
        best_detected_box_conf = best_detected_box.conf[0].item()
        best_detected_box_name = class_names[best_detected_box_id]
        best_detected_box_x1, best_detected_box_y1, best_detected_box_x2, best_detected_box_y2 = best_detected_box.xyxy[0].tolist()
        
        if is_print == True:
            print(f"Customized Printing - Detected '{box_name}' box with best confidence: {best_detected_box_name} with {best_detected_box_conf:.2f} confidence at [{best_detected_box_x1}, {best_detected_box_y1}, {best_detected_box_x2}, {best_detected_box_y2}]")
    else:
        best_detected_box = None
        if is_print == True:
            print(f"Customized Printing - No '{box_name}' box found.")

    return best_detected_box



# ========================================
# Main function integrating vision and IMU
# ========================================

def main():

    # Voting Queue to store the last 3 frames
    voting_queue = deque(maxlen=3)
    voting_required_percentage = 0.5

    l_conf_threshold=0.5
    b_conf_threshold=0.5
    s_conf_threshold=0.4

    voice = Voice("piper.onnx")
    def voice_worker():
        while True:
            text = voice_queue.get() # Block until an item is available
            voice.speak(text)
            voice_queue.task_done()
    threading.Thread(target=voice_worker, daemon=True).start()
    count = 0

    # Load YOLO model
    l_model = YOLO('bestlights.pt')
    b_model = YOLO('bestbulbs.pt')
    s_model = YOLO('bestsigns.pt') 

    # Start video stream
    # cap = cv2.VideoCapture(0)
    # alternatively, use a video file 
    cap = cv2.VideoCapture('videoTest/IMG_1411.mov')
    # cap = cv2.VideoCapture('videoTest/IMG_8767.mp4') # for speed limit sign

    voice.speak("Recording started!")

    #initial
    is_red_traffic_light = False
    is_stop_sign = False
    #is_speed_limit_sign = False
    blinker_on = False


    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        if (count % 5 == 0):
            # Result ID require values:
            # 1. Red/Green light
            # 2. Stop sign
            # 3. * Speed limit sign
            # Scenario1: Driving up to intersection where there are three lights, currently all green
            # Example (error included): R0 for current frame, but the last two were G0 and G0 so still green            
            # Scenario2: Driving up to intersection where there are three lights, currently all red
            result_id = ""
            # =================================
            # Traffic Lights Detection via YOLO
            # go, goLeft, stop, stopLeft, warning, warningLeft
            # =================================

            # Detect traffic lights
            l_results = l_model(frame)   
            l_class_names = l_model.names            
            #frame = l_results[0].plot(img=frame, line_width=2) 

            detected_traffic_light_rgy_confs = []
            for l_box in l_results[0].boxes:
                if l_box.conf[0] > l_conf_threshold:

                    # Extract details  
                    box_conf = l_box.conf[0].item()
                    x1, y1, x2, y2 = map(int, l_box.xyxy[0])
                    x, y, w, h = map(int, l_box.xywh[0])
                    box_id = int(l_box.cls[0].item())               
                    box_name = l_class_names[box_id]
                    print(f"Customized Printing - Detected traffic light with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")
                
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    
                    # crop the image to the traffic light
                    cropped_traffic_light_frame = crop_image(frame, (x - w/2, y - h/2, w, h))
                    
                    # Calculate the crop to original offsets
                    offset_x = int(x - w/2)
                    offset_y = int(y - h/2)
                    
                    cropped_traffic_light_frame = cv2.resize(cropped_traffic_light_frame, 
                                                # (width, height)
                                                (cropped_traffic_light_frame.shape[1], cropped_traffic_light_frame.shape[0]), 
                                                # cv2.INTER_CUBIC for better quality
                                                interpolation=cv2.INTER_CUBIC  
                                                )
                    

                    # Identify the bulb in the cropped image
                    b_results = b_model(cropped_traffic_light_frame)
                    cropped_traffic_light_frame = b_results[0].plot(line_width=1)  
                    #cv2.imshow("Cropped Frame", cropped_traffic_light_frame)   

                    b_class_names = b_model.names       

                    best_red_bulb_box = detect_best_box(b_class_names, b_results[0].boxes, "stop", "contain", b_conf_threshold, False)                        
                    best_green_bulb_box = detect_best_box(b_class_names, b_results[0].boxes, "go", "contain", b_conf_threshold, False)
                    #best_yellow_bulb_box = detect_best_box(b_class_names, b_results[0].boxes, "warning", "contain", 0.5, False)


                    detected_traffic_light_rgy_conf = {'red': 0, 'green': 0, 'yellow': 0}                   
                    if best_red_bulb_box != None:
                        detected_traffic_light_rgy_conf['red'] = best_red_bulb_box.conf[0].item()                    
                    if best_green_bulb_box != None:
                        detected_traffic_light_rgy_conf['green'] = best_green_bulb_box.conf[0].item()
                    #if best_yellow_bulb_box != None:
                    #    detected_traffic_light_rgy_conf['yellow'] = best_yellow_bulb_box.conf[0].item()
                   
                    # determine the color and label
                    is_red = detected_traffic_light_rgy_conf['red'] !=0 and detected_traffic_light_rgy_conf['red'] >= detected_traffic_light_rgy_conf['green']
                    is_green = detected_traffic_light_rgy_conf['green'] !=0 and detected_traffic_light_rgy_conf['green'] > detected_traffic_light_rgy_conf['red'] 
                    label = "Red" if is_red else "Green" if is_green else ""

                    if is_red and result_id == "":
                        result_id = "R"

                    # extract the bounding box coordinates
                    if is_red and best_red_bulb_box != None:
                        bx1, by1, bx2, by2 = best_red_bulb_box.xyxy[0].tolist()
                    elif is_green and best_green_bulb_box != None:
                        bx1, by1, bx2, by2 = best_green_bulb_box.xyxy[0].tolist()
                    else:
                        continue
                    # adjust the coordinates to the original frame
                    traffic_bulb_x1 = int(bx1 + offset_x)
                    traffic_bulb_y1 = int(by1 + offset_y)
                    traffic_bulb_x2 = int(bx2 + offset_x)
                    traffic_bulb_y2 = int(by2 + offset_y)

                    # Draw the bounding box and label on the original frame over just the bulb
                    if is_red:
                        cv2.rectangle(frame, (traffic_bulb_x1, traffic_bulb_y1), (traffic_bulb_x2, traffic_bulb_y2), (0, 0, 255), 2)
                        cv2.putText(frame, label, (int(traffic_bulb_x2), int(traffic_bulb_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    if is_green:
                        cv2.rectangle(frame, (traffic_bulb_x1, traffic_bulb_y1), (traffic_bulb_x2, traffic_bulb_y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (int(traffic_bulb_x2), int(traffic_bulb_y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    detected_traffic_light_rgy_confs.append(detected_traffic_light_rgy_conf)

                    #for b_box in b_results[0].boxes:
                    #    if (b_box.conf[0].item() > 0.7): 
                    #        # Extract details                                    
                    #        bulb_id = int(b_box.cls[0].item())
                    #        bulb_conf = b_box.conf[0].item()
                    #        bulb_name= b_results[0].names[bulb_id]
                    #        bulb_x1, bulb_y1, bulb_x2, bulb_y2 = b_box.xyxy[0].tolist()  
                    #        print(f"Customized Printing - Detected traffic bulb: {bulb_name} with {bulb_conf:.2f} confidence at [{bulb_x1}, {bulb_y1}, {bulb_x2}, {bulb_y2}]")
                    #        if ((bulb_name == 'go' or bulb_name == 'goLeft') and compare_red_green_conf['green'] < bulb_conf):
                    #            compare_red_green_conf['green'] = bulb_conf
                    #        elif ((bulb_name == 'stop' or bulb_name == "stopLeft") and compare_red_green_conf['red'] < bulb_conf):
                    #            compare_red_green_conf['red'] = bulb_conf
                    #detected_traffic_lights.append(compare_red_green_conf)             
                

            # =====================================
            # Traffic Signs Detection via YOLO
            # stop/stopAhead Signs
            # Speed Limit Sign: Passive Reminding using GPS sensor
            # ======================================

            # Detect traffic signs
            s_results = s_model(frame)             
            s_class_names = s_model.names
            #frame = s_results[0].plot(img=frame, line_width=2) 


            # Loop each box to find best Stop sign and Speed Limit sign
            best_speed_limit_value = 0
            best_speed_limit_conf = 0
            best_stop_conf = 0
            best_stop_sign_box = None
            for s_box in s_results[0].boxes:
                if s_box.conf[0] > s_conf_threshold:
                    box_conf = s_box.conf[0].item()
                    x1, y1, x2, y2 = map(int, s_box.xyxy[0])
                    x, y, w, h = map(int, s_box.xywh[0])
                    box_id = int(s_box.cls[0].item())               
                    box_name = s_class_names[box_id]
                    #print(f"Customized Printing - Detected traffic sign with {box_conf:.2f} confidence at [{x1}, {y1}, {x2}, {y2}] with weight {w} and height {h}")

                    
                    # Stop Sign
                    if box_name.lower() == "stop":
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        
                        if box_conf>= best_stop_conf:
                            best_stop_sign_box = s_box
                            best_stop_conf = s_box.conf[0].item()
                            print(f"Customized Printing - Best Stop sign with conf value: {best_stop_conf}")

                        

                    # other signs
                    else: 
                        # Speed Limit Sign
                        # Crop the detected region from the frame
                        cropped = frame[y1:y2, x1:x2]

                        # Optional: Preprocess the cropped image for better OCR
                        #gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                        #_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                        lowercase_text= pytesseract.image_to_string(cropped).lower()
                        if 'speed' in lowercase_text and 'limit' in lowercase_text:                                                           
                            # Extract the first number (e.g., 50)
                            match = re.search(r'\b\d{1,2}\b', lowercase_text)
                            if match and box_conf >= best_speed_limit_conf:                    
                                best_speed_limit_conf = s_box.conf[0].item()
                                best_speed_limit_value = int(match.group())
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                cv2.putText(frame, f'speedLimit{best_speed_limit_value} {box_conf:.2f}', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                                print(f"Customized Printing - Extracted speed limit: {best_speed_limit_value} with conf value: {best_speed_limit_conf} ")
                                    
                                gps.update()
                                current = time.monotonic()
                                if current - last_print >= 1.0:
                                    last_print = current
                                    if not gps.has_fix:
                                        print('Waiting for fix...')
                                    else:
                                        print('=' * 40)  # Print a separator line.
                                        print('Latitude: {0:.6f} degrees'.format(gps.latitude))
                                        print('Longitude: {0:.6f} degrees'.format(gps.longitude))

                                        # Get the speed
                                        if gps.speed_knots is not None:
                                            mph = gps.speed_knots * 1.15078
                                            print('Speed: {0:.2f} mph'.format(mph))

                                            # Check if the speed exceeds the limit
                                            if mph > best_speed_limit_value:
                                                voice.speak("Slow down!")
                                        else:
                                            print('Speed: Not available')
            # =====================================
            # Turning Signal Detection via accelerometer sensor and microphone
            # ==========================================
            # Get accelerometer data
            # direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz = get_direction_and_acceleration()
            # print(f"Accel -> Direction: {direction}, Accel: {accel_magnitude:.2f}, "
            #     f"Ax: {(Ax+Ax_offset):.2f}, Ay: {(Ay+Ay_offset):.2f}, Az: {(Az+Az_offset):.2f}")
            # Example: if moving forward with high acceleration (indicating speeding), warn to slow down
            detected_turn = detect_turn()
            print(f"Detected Turn: {detected_turn}")
            if not blinker_on and detected_turn != "Straight":
                voice.speak(f"Don't forget to turn on your turn signal when turning!")
            
            # if direction == "Forward" and accel_magnitude > 1.5:
            #     voice.speak("Slow down!")
            
            # ==========Optional=================
            # Seat Belt
            # ==========================================

            
            # =======================================
            # Trigger Voice Feedback Based on Analysis
            # ========================================

            # -------traffic light---------
            prev_is_red_traffic_light = is_red_traffic_light
            
            is_red_traffic_light = False
            for detected_traffic_light_rgy_conf in detected_traffic_light_rgy_confs:
                print("Customized Printing - Red Light Conf:" + str(detected_traffic_light_rgy_conf["red"]) + " vs Green Light Conf:" + str(detected_traffic_light_rgy_conf["green"]))
                if (detected_traffic_light_rgy_conf["red"] >= detected_traffic_light_rgy_conf["green"]):
                    is_red_traffic_light = True                 
                
            if (is_red_traffic_light and not prev_is_red_traffic_light):
                # speak_async(voice, "red light detected")
                speak_queued("red light detected")
            elif (not is_red_traffic_light and prev_is_red_traffic_light):
                # speak_async(voice, "red light no longer detected")
                speak_queued("red light no longer detected")

            # -------end of traffic light-----------------
            

            # -------stop sign---------
            prev_is_stop_sign = is_stop_sign

            is_stop_sign = False
            if best_stop_sign_box != None:
                is_stop_sign = True

            #if (is_stop_sign and not prev_is_stop_sign):
            #    speak_async(voice, "stop sign detected")
            #elif (not is_stop_sign and prev_is_stop_sign):
            #    speak_async(voice, "stop sign no longer detected")

            # -------end of stop sign------------------------------


            # -------speed limit sign: Passive reminding---------
            if best_speed_limit_value != None:
                #To do: get speed using GPS module
                driving_speed = 40
            #   if driving_speed > best_speed_limit_value:
            #       speak_async(voice, "Speed limit is " + best_speed_limit_value + ". Your current speed is " + driving_speed + ". Please slow down.")    
                  
            # -------end of speed limit sign------------------------------
            

            #sets up a named window with full-screen support
            cv2.namedWindow("Annotated Frame", cv2.WND_PROP_FULLSCREEN)
            #actually makes it full screen
            cv2.setWindowProperty("Annotated Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Annotated Frame", frame)
            # cv2.imwrite("annotated_frame.jpg", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if (count % 5 == 0):
                # Small delay to ease CPU load
                sleep(0.17)  

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()