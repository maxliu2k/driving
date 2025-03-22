import 'package:camera/camera.dart';
import 'package:pytorch_lite/pytorch_lite.dart';

// Global variables for the three models.
ModelObjectDetection? modelBulbs;
ModelObjectDetection? modelLights;
ModelObjectDetection? modelSigns;

// Function to load the models.
Future<void> loadModels() async {
  try {
    // Load bestbulbs.torchscript
    modelBulbs = await PytorchLite.loadObjectDetectionModel(
      'assets/models/bestbulbs.torchscript',
      6,
      640,
      640,
      labelPath: 'assets/labels/labels_bulbs.txt',
      objectDetectionModelType: ObjectDetectionModelType.yolov8
    );
    // Load bestlights.torchscript
    modelLights = await PytorchLite.loadObjectDetectionModel(
      'assets/models/bestlights.torchscript',
      7,
      640,
      640,
      labelPath: 'assets/labels/labels_lights.txt',
      objectDetectionModelType: ObjectDetectionModelType.yolov8
    );
    // Load bestsigns.torchscript
    modelSigns = await PytorchLite.loadObjectDetectionModel(
      'assets/models/bestsigns.torchscript',
      18,
      640,
      640,
      labelPath: 'assets/labels/labels_signs.txt',
      objectDetectionModelType: ObjectDetectionModelType.yolov8
    );
    print('Models loaded successfully');
  } catch (e) {
    print('Error loading models: $e');
  }
}

// Process the given image from the camera stream and run predictions on it.
Future<void> processFrame(CameraImage image, int rotation) async {
  //check the models are loaded
  if (modelBulbs == null || modelLights == null || modelSigns == null) {
    await loadModels();
  }

  // Predict using the loaded models
  if (modelBulbs != null) {
    try {
      List<ResultObjectDetection>? detectedBulbs = await modelBulbs!.getCameraImagePrediction(
        image,
        rotation: rotation,
        minimumScore: 0.1,
        iOUThreshold: 0.3
      );
      print('Detected bulbs: $detectedBulbs');
    } catch (e) {
      print('Error predicting bulbs: $e');
    }
  }
  if (modelLights != null) {
    try {
      List<ResultObjectDetection>? detectedLights = await modelLights!.getCameraImagePrediction(
        image,
        rotation: rotation,
        minimumScore: 0.1,
        iOUThreshold: 0.3
      );
      print('Detected lights: $detectedLights');
    } catch (e) {
      print('Error predicting lights: $e');
    }
  }
  if (modelSigns != null) {
    try {
      List<ResultObjectDetection>? detectedSigns = await modelSigns!.getCameraImagePrediction(
        image,
        rotation: rotation,
        minimumScore: 0.1,
        iOUThreshold: 0.3
      );
      print('Detected signs: $detectedSigns');
    } catch (e) {
      print('Error predicting signs: $e');
    }
  }
}