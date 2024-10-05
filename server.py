import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import torch
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Load the model
lights_model_path = 'bestlights.pt'
signs_model_path = 'bestsigns.pt'

lights_model = YOLO(lights_model_path)
signs_model = YOLO(signs_model_path)

@app.route('/predict', methods=['POST'])
def predict():
    # Perform a quick check
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400

    # Get the image from the request
    image = request.files['file']

    print('Received image')

    try:
        # Load the image
        image = Image.open(BytesIO(image.read()))

        # Perform the prediction
        lights_results = lights_model([image])
        signs_results = signs_model([image])

        # Extract the predictions
        lights_predictions = lights_results[0].boxes
        signs_predictions = signs_results[0].boxes

        # Prepare the response
        response = {
            "predictions": []
        }

        for pred in lights_predictions:
            response["predictions"].append({
                "class": lights_model.names[int(pred.cls)],
                "confidence": float(pred.conf),
            })

        for pred in signs_predictions:
            response["predictions"].append({
                "class": signs_model.names[int(pred.cls)],
                "confidence": float(pred.conf),
            })

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)