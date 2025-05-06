#???How to use simshow function to show in one window
#???How to debug mode
#???For speedLimit sign, is it possible to extract number from image.

#from voice import Voice
import cv2
from ultralytics import YOLO
from utils import *
#import smbus
from time import sleep
import math
import threading


def speak_async(voice, text):
    threading.Thread(target=voice.speak, args=(text,), daemon=True).start()


"""
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
"""

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

    conf_threshold=0.7

    #voice = Voice("piper.onnx")
    count = 0

    # Load YOLO model
    l_model = YOLO('bestlights.pt')
    b_model = YOLO('bestbulbs.pt')
    s_model = YOLO('bestsigns.pt') 

    # Start video stream
    # cap = cv2.VideoCapture(0)
    # alternatively, use a video file 
    cap = cv2.VideoCapture('videoTest/IMG_1411.mov')

    #voice.speak("Recording started!")

    #initial
    is_red_traffic_light = False
    is_stop_sign = False
    #is_speed_limit_sign = False


    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        if (count % 5 == 0):

            # =================================
            # Traffic Lights Detection via YOLO
            # go, goLeft, stop, stopLeft, warning, warningLeft
            # =================================

            # Detect traffic lights
            l_results = l_model(frame)                 
            frame = l_results[0].plot(img=frame, line_width=2) 

            detected_traffic_lights = []
            for l_box in l_results[0].boxes:
                if l_box.conf[0] > conf_threshold:
                    # Extract details                                    
                    traffic_light_conf = l_box.conf[0].item()
                    traffic_light_x1, traffic_light_y1, traffic_light_x2, traffic_light_y2 = l_box.xyxy[0]
                    traffic_light_x, traffic_light_y, traffic_light_w, traffic_light_h = l_box.xywh[0]
                    print(f"Customized Printing - Detected traffic light with {traffic_light_conf:.2f} confidence at [{traffic_light_x1}, {traffic_light_y1}, {traffic_light_x2}, {traffic_light_y2}] with weight {traffic_light_w} and height {traffic_light_h}")


                    # crop the image to the traffic light
                    cropped_traffic_light_frame = crop_image(frame, (traffic_light_x - traffic_light_w/2, traffic_light_y - traffic_light_h/2, traffic_light_w, traffic_light_h))
                    
                    # Calculate the crop to original offsets
                    offset_x = int(traffic_light_x - traffic_light_w/2)
                    offset_y = int(traffic_light_y - traffic_light_h/2)
                    
                    cropped_traffic_light_frame = cv2.resize(cropped_traffic_light_frame, 
                                                # (width, height)
                                                (cropped_traffic_light_frame.shape[1], cropped_traffic_light_frame.shape[0]), 
                                                # cv2.INTER_CUBIC for better quality
                                                interpolation=cv2.INTER_CUBIC  
                                                )
                    

                    # Identify the bulb in the cropped image
                    b_results = b_model(cropped_traffic_light_frame)
                    cropped_traffic_light_frame = b_results[0].plot(line_width=1)  
                    # cv2.imshow("Cropped Frame", cropped_traffic_light_frame)   

                    b_class_names = b_model.names                               

                    compare_red_green_conf = {'red': 0, 'green': 0}

                    best_red_bulb_box = detect_best_box(b_class_names, b_results[0].boxes, "stop", "contain", conf_threshold, False)
                    if best_red_bulb_box != None:
                        compare_red_green_conf['red'] = best_red_bulb_box.conf[0].item()

                    best_green_bulb_box = detect_best_box(b_class_names, b_results[0].boxes, "go", "contain", conf_threshold, False)
                    if best_green_bulb_box != None:
                        compare_red_green_conf['green'] = best_green_bulb_box.conf[0].item()

                    detected_traffic_lights.append(compare_red_green_conf)

                    for compare_red_green_conf in detected_traffic_lights:
                        # determine the color and lable
                        is_red = compare_red_green_conf['red'] >= compare_red_green_conf['green']
                        label = "Red" if is_red else "Green"

                        # extract the bounding box coordinates
                        if is_red and best_red_bulb_box != None:
                            bx1, by1, bx2, by2 = best_red_bulb_box.xyxy[0].tolist()
                        elif not is_red and best_green_bulb_box != None:
                            bx1, by1, bx2, by2 = best_green_bulb_box.xyxy[0].tolist()
                        else:
                            continue
                        # adjust the coordinates to the original frame
                        traffic_light_x1 = int(bx1 + offset_x)
                        traffic_light_y1 = int(by1 + offset_y)
                        traffic_light_x2 = int(bx2 + offset_x)
                        traffic_light_y2 = int(by2 + offset_y)

                        # Draw the bounding box and label on the original frame over just the bulb
                        cv2.rectangle(frame, (traffic_light_x1, traffic_light_y1), (traffic_light_x2, traffic_light_y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (int(traffic_light_x1), int(traffic_light_y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)



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
                    #        detected_traffic_lights.append(compare_red_green_conf)             

            
            # =====================================
            # Traffic Signs Detection via YOLO
            # stop/stopAhead Signs
            # Speed Limit Sign: Passive Reminding using GPS sensor
            # ======================================

            # Detect traffic signs
            s_results = s_model(frame) 
        
            s_class_names = s_model.names

            # best stop sign        
            best_stop_sign_box = detect_best_box(s_class_names, s_results[0].boxes, "stop", "equal", conf_threshold, True)

            # best speed limit sign
            best_speed_limit_sign_box = detect_best_box(s_class_names, s_results[0].boxes, "speedLimit", "contain", conf_threshold, True)
            
                  
            # =====================================
            # Turning Signal Detection via accelerometer sensor and microphone
            # ==========================================
  
            # Get accelerometer data
            # direction, accel_magnitude, Ax, Ay, Az, Gx, Gy, Gz = get_direction_and_acceleration()
            # print(f"Accel -> Direction: {direction}, Accel: {accel_magnitude:.2f}, "
            #     f"Ax: {(Ax+Ax_offset):.2f}, Ay: {(Ay+Ay_offset):.2f}, Az: {(Az+Az_offset):.2f}")
            # Example: if moving forward with high acceleration (indicating speeding), warn to slow down
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
            for compare_red_green_conf in detected_traffic_lights:
                print("Customized Printing - Red Light Conf:" + str(compare_red_green_conf["red"]) + " vs Green Light Conf:" + str(compare_red_green_conf["green"]))
                if (compare_red_green_conf["red"] >= compare_red_green_conf["green"]):
                    is_red_traffic_light = True                 
                
            #if (is_red_traffic_light and not prev_is_red_traffic_light):
            #    speak_async(voice, "red light detected")
            #elif (not is_red_traffic_light and prev_is_red_traffic_light):
            #    speak_async(voice, "red light no longer detected")
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
            if best_speed_limit_sign_box != None:
                #To do: get speed using GPS module
                driving_speed = 40
                best_speed_limit_sign_box_speed_value = int(s_class_names[int(best_speed_limit_sign_box.cls[0].item())].replace("speedLimit", ""))
            #    if driving_speed > best_speed_limit_sign_box_speed_value:
            #        speak_async(voice, "Speed limit is " + best_speed_limit_sign_box_speed_value + ". Your current speed is " + driving_speed + ". Please slow down.")          
            # -------end of speed limit sign------------------------------
            
      
            
            frame = s_results[0].plot(img=frame, line_width=2)   

            #sets up a named window with full-screen support
            #cv2.namedWindow("Annotated Frame", cv2.WND_PROP_FULLSCREEN)
            #actually makes it full screen
            #cv2.setWindowProperty("Annotated Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
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