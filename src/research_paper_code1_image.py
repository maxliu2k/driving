import os
import shutil
from ultralytics import YOLO

# ===============================
# Image Model
# ===============================

# Train a YOLOv8 model with given dataset and parameters.
def train_yolo_model(best_model_save_to_path, 
                     yaml_path, project, 
                     epochs=100, batch=32, imgsz=640, 
                     save_period=10, patience=20, close_mosaic=10, 
                     cos_lr=True, device=0, workers=2, cache=True, seed=0,
                     hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, 
                     degrees=0.0, translate=0.1, scale=0.5, shear=0.0, perspective=0.0,
                     flipud=0.0, fliplr=0.5, 
                     bgr=0.0, mosaic=1.0, mixup=0.0, cutmix=0.0):
     
    # Load a pretrained YOLOv8 model
    model = YOLO("yolov8n.pt")

    # Train the model
    model.train(data=yaml_path, project=project, 
                epochs=epochs, batch=batch, imgsz=imgsz,
                save_period=save_period, patience=patience, close_mosaic=close_mosaic, 
                cos_lr=cos_lr, device=device, workers=workers, cache=cache, seed=seed,
                hsv_h=hsv_h, hsv_s=hsv_s, hsv_v=hsv_v,
                degrees=degrees, translate=translate, scale=scale, shear=shear, perspective=perspective,
                flipud=flipud, fliplr=fliplr,
                bgr=bgr, mosaic=mosaic, mixup=mixup, cutmix=cutmix)

    # Copy best.pt to specified path
    best_model_path = os.path.join(os.path.join(project, os.listdir(project)[-1]), "weights", "best.pt")
    os.makedirs(os.path.dirname(best_model_save_to_path), exist_ok=True)
    shutil.copy(best_model_path, best_model_save_to_path)


def main():
    # Train traffic light model
    l_yaml = "dataset/traffic_light/data.yaml"
    l_results = "results/traffic_light"
    l_best_model_save_to_path = "models/image/best_light.pt"
    train_yolo_model(best_model_save_to_path=l_best_model_save_to_path, 
                    data_yaml=l_yaml, project=l_results,
                    hsv_h=0.0, hsv_s=0.4, 
                    degrees=5, scale=0.3,
                    fliplr=0.2,
                    mosaic=0.5)
    
    # Train traffic bulb model
    b_yaml = "dataset/traffic_bulbs/data.yaml"
    b_results = "results/traffic_bulbs"
    b_best_model_save_to_path = "models/image/best_bulb.pt"
    train_yolo_model(best_model_save_to_path=b_best_model_save_to_path, 
                    data_yaml=b_yaml, project=b_results,
                    hsv_h=0.0, hsv_s=0.4, 
                    scale=0.15,
                    fliplr=0.0,
                    mosaic=0.2)
    
    # Train traffic sign model
    s_yaml = "dataset/traffic_signs/data.yaml"
    s_results = "results/traffic_signs"
    s_best_model_save_to_path = "models/image/best_sign.pt"
    train_yolo_model(best_model_save_to_path=s_best_model_save_to_path, 
                    data_yaml=s_yaml, project=s_results,
                    hsv_h=0.0, hsv_s=0.2, hsv_v=0.2, 
                    degrees=5, scale=0.3,
                    fliplr=0.0,
                    mosaic=0.2)
    

if __name__ == "__main__":
    main()
