import 'dart:async';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:developer' as developer; // Import for logging
import 'brightness_controller.dart';
import 'network_client.dart';
import 'state_manager.dart';

class CameraServices {
  static bool isStreaming = false;
  static bool isCapturing = false; // Flag to check if an image capture is in progress
  static int _imagesCaptured = 0;
  static int _lastLogTimestamp = DateTime.now().millisecondsSinceEpoch;
  static BrightnessController? _brightnessController;

  static Future<void> streamCameraFootage(CameraController controller, StateManager stateManager, {int frameIntervalMs = 50}) async {
    if (isStreaming) {
      developer.log('Camera is already streaming', name: 'camera.info');
      return;
    }

    _brightnessController = BrightnessController();
    _brightnessController?.setBrightnessToMax();
    _brightnessController?.startListening();

    NetworkClient networkClient = NetworkClient();
    isStreaming = true;

    int lastTimestamp = DateTime.now().millisecondsSinceEpoch;
    String imageFormat = controller.imageFormatGroup.toString();
    developer.log('Camera image format: $imageFormat', name: 'camera.info');

    controller.startImageStream((CameraImage image) async {
      if (isStreaming) {
        int currentTimestamp = DateTime.now().millisecondsSinceEpoch;
        if (currentTimestamp - lastTimestamp >= frameIntervalMs) {
          lastTimestamp = currentTimestamp;

          int? luxValue = _brightnessController?.getLatestLuxValue();
          developer.log('Lux value: $luxValue', name: 'camera.info');

          sendImageOverTCP(image, networkClient, stateManager, currentTimestamp);
          saveImageLocally(controller);  // Save the image locally using the modified method
        }
      }
    });
  }

  static void sendImageOverTCP(CameraImage image, NetworkClient networkClient, StateManager stateManager, int currentTimestamp) {
    // Method implementation remains unchanged
  }

  static Future<void> saveImageLocally(CameraController controller) async {
    if (isCapturing) return; // Exit if a capture is already in progress

    isCapturing = true;
    try {
      final XFile file = await controller.takePicture();
      final Directory? directory = await getExternalStorageDirectory();

      final String filePath = '${directory?.path}/${DateTime.now().millisecondsSinceEpoch}.jpg';

      await file.saveTo(filePath); // Saves the image captured by the camera to the specified path
      developer.log('Image saved to $filePath', name: 'camera.save');
    } catch (e) {
      developer.log('Error saving image locally: $e', name: 'camera.error');
    } finally {
      isCapturing = false; // Reset the flag after operation completes
    }
  }
}
