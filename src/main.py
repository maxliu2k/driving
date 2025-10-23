import cv2
from ultralytics import YOLO
import threading
import random
from datetime import datetime
from time import sleep
import queue
from collections import deque
#import pynmea2 #pip install pyserial pynmea2

from utils import *
from speed_limit_OCR import SpeedLimitOCR
from turn_signal_detection_manager import TurnSignalDetectionManager
from voice_playback_manager import VoicePlaybackManager
from IMU_controller import IMUController
from GPS_controller import GPSController

def is_bbox_stable(bbox1, bbox2):
    x1_min, y1_min, x1_max, y1_max = bbox1
    x2_min, y2_min, x2_max, y2_max = bbox2

    inter_x1, inter_y1 = max(x1_min, x2_min), max(y1_min, y2_min)
    inter_x2, inter_y2 = min(x1_max, x2_max), min(y1_max, y2_max)

    inter_width = max(0, inter_x2 - inter_x1)
    inter_height = max(0, inter_y2 - inter_y1)

    inter_area = inter_width * inter_height

    if inter_area == 0:
        return 0.0

    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)

    return inter_area / (area1 + area2 - inter_area)

# Process a single detected traffic light box and update confidence values and detected box lists for each color and direction
def process_rgy_box(
    b_box, b_box_conf, b_box_name,
    best_rgy_conf, best_rgy_left_conf, best_rgy_right_conf,
    detected_rgy_boxes, detected_rgy_left_boxes, detected_rgy_right_boxes
):
    match b_box_name:
        case "stop":
            if b_box_conf > best_rgy_conf['red']:
                best_rgy_conf['red'] = b_box_conf
            detected_rgy_boxes['red'].append((b_box, b_box_name))

        case "stopLeft":
            if b_box_conf > best_rgy_left_conf['red']:
                best_rgy_left_conf['red'] = b_box_conf
            detected_rgy_left_boxes['red'].append((b_box, b_box_name))

        case "stopRight":
            if b_box_conf > best_rgy_right_conf['red']:
                best_rgy_right_conf['red'] = b_box_conf
            detected_rgy_right_boxes['red'].append((b_box, b_box_name))

        case "go":
            if b_box_conf > best_rgy_conf['green']:
                best_rgy_conf['green'] = b_box_conf
            detected_rgy_boxes['green'].append((b_box, b_box_name))

        case "goLeft":
            if b_box_conf > best_rgy_left_conf['green']:
                best_rgy_left_conf['green'] = b_box_conf
            detected_rgy_left_boxes['green'].append((b_box, b_box_name))

        case "goRight":
            if b_box_conf > best_rgy_right_conf['green']:
                best_rgy_right_conf['green'] = b_box_conf
            detected_rgy_right_boxes['green'].append((b_box, b_box_name))

        case "warning":
            if b_box_conf > best_rgy_conf['yellow']:
                best_rgy_conf['yellow'] = b_box_conf
            detected_rgy_boxes['yellow'].append((b_box, b_box_name))

        case "warningLeft":
            if b_box_conf > best_rgy_left_conf['yellow']:
                best_rgy_left_conf['yellow'] = b_box_conf
            detected_rgy_left_boxes['yellow'].append((b_box, b_box_name))

        case "warningRight":
            if b_box_conf > best_rgy_right_conf['yellow']:
                best_rgy_right_conf['yellow'] = b_box_conf
            detected_rgy_right_boxes['yellow'].append((b_box, b_box_name))


# Determine the dominant color for forward, left, and right directions
def get_dominant_color_for_direction(
    best_rgy_conf, best_rgy_left_conf, best_rgy_right_conf,
    detected_rgy_boxes, detected_rgy_left_boxes, detected_rgy_right_boxes,
    diff_conf):

    dominant_color_box_list = []  # single list of tuples: (box, box_name)
    dominant_color = {}

    def process_conf(best_conf, detected_boxes, direction):
        for color, conf_value in best_conf.items():
            if all(conf_value >= other_val + diff_conf
                   for other_color, other_val in best_conf.items() if other_color != color):
                dominant_color[direction] = color
                dominant_color_box_list.extend(detected_boxes[color])
                # for box in detected_boxes[color]:
                #     box_id = int(box.cls[0].item())
                #     box_name = b_class_names[box_id].lower()
                #     dominant_color_box_list.append((box, box_name))

    process_conf(best_rgy_conf, detected_rgy_boxes, "forward")
    process_conf(best_rgy_left_conf, detected_rgy_left_boxes, "left")
    process_conf(best_rgy_right_conf, detected_rgy_right_boxes, "right")

    return dominant_color, dominant_color_box_list


# Analyze all detected traffic light boxes to determine the dominant color
#(red, yellow, green) for forward, left-turn, and right-turn directions.
def analyze_light_bulbs(b_results, b_class_names, b_conf_threshold, diff_conf):

    # Initialize confidence and box containers
    conf = {
        "forward": {'red': 0, 'yellow': 0, 'green': 0},
        "left":    {'red': 0, 'yellow': 0, 'green': 0},
        "right":   {'red': 0, 'yellow': 0, 'green': 0},
    }
    boxes = {
        "forward": {'red': [], 'yellow': [], 'green': []},
        "left":    {'red': [], 'yellow': [], 'green': []},
        "right":   {'red': [], 'yellow': [], 'green': []},
    }

    # Map class names to direction and color
    mapping = {
        "stop": ("forward", "red"),
        "stopLeft": ("left", "red"),
        "stopRight": ("right", "red"),
        "warning": ("forward", "yellow"),
        "warningLeft": ("left", "yellow"),
        "warningRight": ("right", "yellow"),
        "go": ("forward", "green"),
        "goLeft": ("left", "green"),
        "goRight": ("right", "green"),
    }

    # Process all detected boxes
    for b_box in b_results[0].boxes:
        b_conf = b_box.conf[0].item()
        if b_conf < b_conf_threshold:
            continue

        b_name = b_class_names[int(b_box.cls[0].item())]
        if b_name not in mapping:
            continue  # skip unknown labels

        direction, color = mapping[b_name]
        boxes[direction][color].append((b_box, b_name))

        # Update best confidence
        if b_conf > conf[direction][color]:
            conf[direction][color] = b_conf

    # Determine dominant colors
    dominant_color = {}
    dominant_color_box_list = []

    for direction, color_conf in conf.items():
        for color, val in color_conf.items():
            if all(val >= other_val + diff_conf
                   for other_color, other_val in color_conf.items() if other_color != color):
                dominant_color[direction] = color
                dominant_color_box_list.extend(boxes[direction][color])

    return dominant_color, dominant_color_box_list

# Plot all boxes in plot_box_list
def plot_boxes(frame, plot_box_list):
    big_font_scale = 0.6  
    small_font_scale = 0.4
    thickness = 2
    for plot_box_item in plot_box_list:
        # Unpack tuple: box, class_name, offset_x, offset_y
        box, box_name, offset_x, offset_y = plot_box_item
        box_conf = box.conf[0].item()
        x1, y1, x2, y2 = map(int, box.xyxy[0])                    

        x1 = int(x1 + offset_x)
        y1 = int(y1 + offset_y)
        x2 = int(x2 + offset_x)
        y2 = int(y2 + offset_y)

        match box_name:
            case "trafficLight":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness)
                cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (255, 0, 0), thickness)
            case "stop":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                cv2.putText(frame, '', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 0, 255), thickness) 
            case "stopLeft":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                cv2.putText(frame, 'left', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 0, 255), thickness)
            case "stopRight":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                cv2.putText(frame, 'right', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 0, 255), thickness)
            case "go":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                cv2.putText(frame, '', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
            case "goLeft":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                cv2.putText(frame, 'left', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
            case "goRight":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                cv2.putText(frame, 'right', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 0), thickness)
            case "warning":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), thickness)
                cv2.putText(frame, '', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness)                           
            case "warningLeft":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), thickness)
                cv2.putText(frame, 'left', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness) 
            case "warningRight":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), thickness)
                cv2.putText(frame, 'right', (int(x2), int(y2) + 10), cv2.FONT_HERSHEY_SIMPLEX, small_font_scale, (0, 255, 255), thickness)     
            case "stop"|"stopAhead"|"yield"|"yieldAhead":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
                cv2.putText(frame, f'{box_name} {box_conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (0, 0, 255), thickness)
            case _:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness)
                cv2.putText(frame, f'speedLimit {box_conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, big_font_scale, (255, 0, 0), thickness)  
    
# ========================================
# Main function
# =============================
# ===========
def main():

    start_time = datetime.now()

    imu_controller = IMUController()
    
    gps_controller = IMUController()

    print("===========================Starting turn signal detection engine...")
    turn_signal_detection_manager = TurnSignalDetectionManager("models/sound/turn_signal_cnn.pt", "cpu")
    turn_signal_detection_manager.start()

    print("===========================Starting voice playback engine...")  
    voice_playback_manager = VoicePlaybackManager("models/voice/piper.onnx")
    voice_playback_manager.start()
  

    # Initialize traffic lights and signs to false
    traffic_control_flag = {
        "RedTrafficLight": False, 
        "RedLeftTurnTrafficLight": False, 
        "RedRightTurnTrafficLight": False, 
        "StopTrafficSign": False, 
        "StopAheadTrafficSign": False, 
        "YieldTrafficSign": False, 
        "YieldAheadTrafficSign": False, 
        "SpeedLimitTrafficSign": False}
    traffic_control_flag_history = deque(maxlen=3)
    for _ in range(3):
        traffic_control_flag_history.append(traffic_control_flag.copy())  

    # traffic_control_name = {
    #     "RedTrafficLight": "red light", 
    #     "RedLeftTurnTrafficLight": "red left turn light",
    #     "RedRightTurnTrafficLight": "red right turn light",
    #     "StopTrafficSign": "stop sign", 
    #     "StopAheadTrafficSign": "stop ahead sign", 
    #     "YieldTrafficSign": "yield sign", 
    #     "YieldAheadTrafficSign": "yield ahead sign", 
    #     "SpeedLimitTrafficSign": "speed limit sign"}
    
    last_confirmed_traffic_control_flag = traffic_control_flag.copy()

    speed_limit_ocr = SpeedLimitOCR(['en'])

    # last_speed_bbox = None
    # last_speed_ocr_frame = -10**9
    # STABILITY_THRESHOLD = 0.5
    # OCR_COOLDOWN_FRAMES = 10

    l_conf_threshold=0.5 
    b_conf_threshold=0.5
    s_conf_threshold=0.4
    speed_limit_ocr_conf_threshold = 80
    diff_conf = 0.1

    # Load YOLO model
    l_model = YOLO('models/image/best_light.pt')
    b_model = YOLO('models/image/best_bulb.pt')
    s_model = YOLO('models/image/best_sign.pt') 

    # Start video stream
    print("===========================Starting video capture...")
    # cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture('tests/video/Demo_1080.mp4')
    cap = cv2.VideoCapture('tests/video/IMG_1409.mov')
    count = 0
    PROCESS_EVERY_N = 10
    while cap.isOpened():
        count += 1
        # Read video frame
        ret, frame = cap.read()
        if not ret:
            break
        
        if (count % PROCESS_EVERY_N== 0):        
            # Each iteration, reset current_traffic_control_flag
            current_traffic_control_flag = traffic_control_flag.copy()
            plot_box_list = []

            # =======================================
            # 1: Traffic Lights Detection via YOLO
            # stop, stopLeft, stopRight, go, goLeft, goRight, warning, warningLeft, warningRight
            # =======================================

            # Detect traffic lights.
            l_results = l_model(frame, verbose=False)   
            l_class_names = l_model.names            

            # For each traffic light
            for l_box in l_results[0].boxes:
                if l_box.conf[0] > l_conf_threshold:                   
                    l_box_name = l_class_names[int(l_box.cls[0].item())]           
                    plot_box_list.append((l_box, l_box_name, 0, 0))

                    # Crop traffic light image box
                    l_x, l_y, l_w, l_h = map(int, l_box.xywh[0])   
                    cropped_traffic_light_frame = crop_image(frame, (l_x - l_w/2, l_y - l_h/2, l_w, l_h))                   
                    cropped_traffic_light_frame = cv2.resize(cropped_traffic_light_frame, 
                                                # (width, height)
                                                (cropped_traffic_light_frame.shape[1], cropped_traffic_light_frame.shape[0]), 
                                                # cv2.INTER_CUBIC for better quality
                                                interpolation=cv2.INTER_CUBIC  
                                                )
                    
                    # Detect light bulbs in the cropped image.
                    b_results = b_model(cropped_traffic_light_frame, verbose=False)
                    b_class_names = b_model.names   
                    
                    # Determine the dominant color for forward, left, and right directions
                    dominant_color, dominant_color_box_list = analyze_light_bulbs(
                        b_results, b_class_names, b_conf_threshold, diff_conf
                    )

                    if dominant_color.get("forward") == "red":
                        current_traffic_control_flag["RedTrafficLight"] = True
                    if dominant_color.get("left") == "red":
                        current_traffic_control_flag["RedLeftTurnTrafficLight"] = True
                    if dominant_color.get("right") == "red":
                        current_traffic_control_flag["RedRightTurnTrafficLight"] = True
                    
                    # Calculate the crop to offsets
                    offset_x = int(l_x - l_w/2)
                    offset_y = int(l_y - l_h/2)
                    plot_box_list.extend([(b_box, b_box_name, offset_x, offset_y) for (b_box, b_box_name) in dominant_color_box_list])

            # =======================================
            # 2: Traffic Signs Detection via YOLO
            # stop, stopAhead, yield, yieldAhead, speedLimit
            # =======================================

            # Detect traffic signs.
            s_results = s_model(frame, verbose=False)          
            s_class_names = s_model.names
            
            # Iterate through all detected traffic signs. 
            best_speed_limit_conf = 0
            best_speed_limit_value = None
            for s_box in s_results[0].boxes:
                if s_box.conf[0] > s_conf_threshold:                                          
                    s_box_name = s_class_names[int(s_box.cls[0].item())]
                    match s_box_name:
                        case "stop":
                            current_traffic_control_flag["StopTrafficSign"]=True
                            plot_box_list.append((s_box, s_box_name, 0, 0))                                                   
                        case "stopAhead":
                            current_traffic_control_flag["StopAheadTrafficSign"]=True
                            plot_box_list.append((s_box, s_box_name, 0, 0))
                        case "yield":
                            current_traffic_control_flag["YieldTrafficSign"]=True
                            plot_box_list.append((s_box, s_box_name, 0, 0))
                        case "yieldAhead":
                            current_traffic_control_flag["YieldAheadTrafficSign"]=True
                            plot_box_list.append((s_box, s_box_name, 0, 0))
                        case _:  
                            s_x1, s_y1, s_x2, s_y2 = map(int, s_box.xyxy[0])                                                      
                            cropped = frame[s_y1:s_y2, s_x1:s_x2]
                            
                            # do_ocr = False
                            # if (last_speed_bbox is not None and is_bbox_stable(last_speed_bbox, s_box) >= STABILITY_THRESHOLD) or (count - last_speed_ocr_frame) >= OCR_COOLDOWN_FRAMES:
                            #     do_ocr = True
                            
                            do_ocr = True
                            if do_ocr:
                                # last_speed_bbox = s_box
                                # last_speed_ocr_frame = count
                                speed_limit_value = speed_limit_ocr.extract_speed_limit(cropped, speed_limit_ocr_conf_threshold)
                                if speed_limit_value is not None:                                                              
                                    current_traffic_control_flag["SpeedLimitTrafficSign"]=True   
                                    plot_box_list.append((s_box, s_box_name, 0, 0)) 
                                    if (s_box_conf := s_box.conf[0].item()) >= best_speed_limit_conf:
                                        best_speed_limit_conf, best_speed_limit_value = s_box_conf, speed_limit_value
                                    # print(f"===========================Extracted speed limit sign value: {speed_limit_value}")  

            traffic_control_flag_history.append(current_traffic_control_flag)

            # =======================================
            # 3: Voice Playback
            # =======================================     
            # Voice triggered when the following traffic signal detected or undetected
            # 1. traffic light: red light, red left turn light, and red right turn light 
            # 2. traffic sign: stop , stop ahead, yield, yield ahead, and speed limit when speeding

            # print([traffic_control_flag_history[i]["SpeedLimitTrafficSign"] for i in range(len(traffic_control_flag_history))])
            # print(last_confirmed_traffic_control_flag["SpeedLimitTrafficSign"])


            # # For demo only
            # do_turn_signal_check = False
            # do_speeding_check = False
            # do_turn_signal_check = (count>=1275 and count<1285) or (count>=1785 and count<1795)
            # do_speeding_check = (count>=2195 and count<2205) or (count>=3395 and count<3405)

            # if best_speed_limit_value is not None:
            #    driving_mph = random.randint(best_speed_limit_value, best_speed_limit_value+5)

            # if do_turn_signal_check:
            #      voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/turn_signal.wav") 
            # 
                                  
            # # End of for Demo

            # Voice Alert for turn signal
            if not turn_signal_detection_manager.is_blinker_on and imu_controller.detect_turn() != "Straight":
                # voice_playback_manager.speak_queued("Do not forget to use your turn signal when turning! ")
                # print("===========================Do not forget to use your turn signal when turning! ")  
               voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/turn_signal.wav") 
            
            # Voice Alert for speeding
            if current_traffic_control_flag["SpeedLimitTrafficSign"] and not last_confirmed_traffic_control_flag["SpeedLimitTrafficSign"]:
                gps_controller.update() 
                driving_mph = gps_controller.get_speed_mph()   
                if best_speed_limit_value is not None and driving_mph > best_speed_limit_value:
                    # voice_playback_manager.speak_queued("You are above the detected speed limit. ") 
                    # print("===========================You are above the detected speed limit. ")                            
                    voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/speed_limit.wav")
                last_confirmed_traffic_control_flag["SpeedLimitTrafficSign"] = current_traffic_control_flag["SpeedLimitTrafficSign"]      

            

            # Voice Alert for others
            for key in current_traffic_control_flag:
                # If a traffic control has been detected three times in a row and was not previously confirmed as detected.                       
                if all(traffic_control_flag_history[i][key] for i in range(3)) and not last_confirmed_traffic_control_flag[key]:

                    #if key in ("RedTrafficLight", "RedLeftTurnTrafficLight", "RedRightTurnTrafficLight", "StopTrafficSign", "StopAheadTrafficSign", "YieldTrafficSign", "YieldAheadTrafficSign"):
                        # voice_playback_manager.speak_queued(f"{traffic_control_name[key]} detected. ")  
                        # print(f"==========================={traffic_control_name[key]} detected. ") 
                    match key:
                        case "RedTrafficLight":
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/red_light.wav")
                        case "RedLeftTurnTrafficLight" :
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/red_left_light.wav")
                        case "StopTrafficSign":
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/stop.wav")
                        case "StopAheadTrafficSign":
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/stop_ahead.wav")
                        case "YieldTrafficSign":
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/yield.wav")
                        case "YieldAheadTrafficSign":
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/yield_ahead.wav")
                

                    last_confirmed_traffic_control_flag[key] = current_traffic_control_flag[key]
                                     
                # If a traffic control has not been detected for three times in a row and was previously confirmed as detected.    
                if all(not traffic_control_flag_history[i][key] for i in range(3)) and last_confirmed_traffic_control_flag[key]:          
                    #if key in ("RedTrafficLight", "RedLeftTurnTrafficLight", "RedRightTurnTrafficLight"):
                        # voice_playback_manager.speak_queued(f"{traffic_control_name[key]} no longer detected.")
                        # print(f"==========================={traffic_control_name[key]} no longer detected.")
                    match key:
                        case "RedTrafficLight":
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/red_light_off.wav")
                        case "RedLeftTurnTrafficLight" :
                            voice_playback_manager.speak_queued("mobile_app/max_driving/assets/audios/red_left_light_off.wav")
                    
                    last_confirmed_traffic_control_flag[key] = current_traffic_control_flag[key]
      

            # =======================================
            # 4: Plotting
            # =======================================
            plot_boxes(frame, plot_box_list)  

            # Set up a named window with full-screen support
            cv2.namedWindow("Annotated Frame", cv2.WND_PROP_FULLSCREEN)
            #cv2.setWindowProperty("Annotated Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Annotated Frame", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if (count % 10 == 0):
               # Small delay to ease CPU load
               sleep(0.20) 

            # print(f"count is {count}, do_speeding_check is {do_speeding_check}, do_turn_signal_check is {do_turn_signal_check}")

    cap.release()
    cv2.destroyAllWindows()

    turn_signal_detection_manager.stop()
    voice_playback_manager.stop()
    
    end_time = datetime.now()
    duration = end_time - start_time
    print("Duration:", duration)
    print("count", count)

if __name__ == "__main__":
    main()