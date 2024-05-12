import 'dart:async';
import 'package:camera/camera.dart';
import 'package:dart/main.dart';
import 'dart:developer' as developer; // Import for logging
import 'dart:typed_data';
import 'brightness_controller.dart';
import 'network_client.dart';
import 'state_manager.dart';


class CameraServices {

  static bool isStreaming = false; // Now a static variable, accessible from anywhere
  static int _imagesCaptured = 0;
  static int _lastLogTimestamp = DateTime.now().millisecondsSinceEpoch;
  static BrightnessController? _brightnessController;


  static Future<void> streamCameraFootage(CameraController controller, StateManager stateManager, {int frameIntervalMs = 250}) async {
    // 50 corresponds to approximately 20 frames per second, test other values as needed

    if (isStreaming) {
      developer.log('Camera is already streaming', name: 'camera.info');
      return; // Already streaming, avoid reinitialization
    }

    _brightnessController = BrightnessController(); // Initialize the brightness controller
    _brightnessController?.setBrightnessToMax(); // Set the brightness to maximum
    _brightnessController?.startListening(); // Start listening with the light sensor

    NetworkClient networkClient = NetworkClient(); // Initialize the network client


    isStreaming = true;

    int lastTimestamp = DateTime.now().millisecondsSinceEpoch;

    // Here we assume that your CameraController has been properly initialized.
    String imageFormat = controller.imageFormatGroup.toString();
    developer.log('Camera image format: $imageFormat', name: 'camera.info');

    controller.startImageStream((CameraImage image) async {
      if (isStreaming) {

        int currentTimestamp = DateTime.now().millisecondsSinceEpoch;
        if (currentTimestamp - lastTimestamp >= frameIntervalMs) {
          lastTimestamp = currentTimestamp;

          // Get the latest lux value
          int? luxValue = _brightnessController?.getLatestLuxValue();
          developer.log('Lux value: $luxValue', name: 'camera.info');

          // Send the image over TCP
          sendImageOverTCP(image, networkClient, stateManager, currentTimestamp);  // Send the image over TCP
          sendBrightnessOverTCP(GlobalVariables.luxValue, networkClient);
          sendTiltAngleOverTCP(GlobalVariables.tiltAngle, networkClient);
        }
      }
    });
    }

    static void sendBrightnessOverTCP(int luxValue, NetworkClient networkClient) {
      // Use ByteData for the conversion to bytes
      ByteData byteData = ByteData(4);
      byteData.setInt32(0, luxValue, Endian.big);
      final Uint8List brightnessHeader = byteData.buffer.asUint8List();
      networkClient.sendBinaryData(brightnessHeader);  // Send the brightness value over TCP
    }

    static void sendTiltAngleOverTCP(double tiltAngle, NetworkClient networkClient) {
      // Convert to integer for sending over TCP
      //print('Tiltangle : ${GlobalVariables.tiltAngle}');
      int tiltAngleInt = tiltAngle.toInt();

      // Use ByteData for the conversion to bytes
      ByteData byteData = ByteData(4);
      byteData.setInt32(0, tiltAngleInt, Endian.big);
      final Uint8List tiltAngleHeader = byteData.buffer.asUint8List();
      networkClient.sendBinaryData(tiltAngleHeader);  // Send the tilt angle over TCP
    }

    //TODO: Make ByteData to a function in network_client.dart
    static void sendImageOverTCP(CameraImage image, NetworkClient networkClient, StateManager stateManager, int currentTimestamp) {
      // Get the current state as an integer
      int stateInt = stateManager.currentState.index;
      //developer.log('Current state: ${stateInt.toString()}');

      // Use ByteData for the conversion to bytes
      ByteData byteDataState = ByteData(4);
      byteDataState.setInt32(0, stateInt, Endian.big);
      final Uint8List stateHeader = byteDataState.buffer.asUint8List();
      networkClient.sendBinaryData(stateHeader);

      // Assuming the image is in NV21 format or similar, consisting of Y plane followed by UV plane
      final Uint8List yPlane = image.planes[0].bytes; // Y plane
      final Uint8List uvPlane = image.planes[1].bytes; // UV plane (assuming NV21 format or similar)
      final int ySize = yPlane.length;
      final int uvSize = uvPlane.length;
      final int totalSize = ySize + uvSize;


      _imagesCaptured++;  // Increment the number of images captured

      if (totalSize > 0) {
        // Prepare and send the total size of the concatenated image data
        final ByteData byteData = ByteData(4);
        byteData.setUint32(0, totalSize, Endian.big);
        final Uint8List sizeHeader = byteData.buffer.asUint8List();
        networkClient.sendBinaryData(sizeHeader);  // Send the total size of the concatenated image data

        // Prepare and send the resolution of the image
        final ByteData resolutionData = ByteData(8);
        resolutionData.setUint32(0, image.width, Endian.big);
        resolutionData.setUint32(4, image.height, Endian.big);
        final Uint8List resolutionHeader = resolutionData.buffer.asUint8List();
        networkClient.sendBinaryData(resolutionHeader);  // Send the resolution of the image (width and height)


        // Concatenate Y and UV data for NV21 format and send
        final Uint8List nv21Data = Uint8List.fromList(yPlane + uvPlane);
        networkClient.sendBinaryData(nv21Data);  // Send the actual concatenated image bytes


        // Logging the number of images captured every second
        if (currentTimestamp - _lastLogTimestamp >= 1000) {
          developer.log('Images captured in last second: $_imagesCaptured', name: 'camera.capture');
          _imagesCaptured = 0;
          _lastLogTimestamp = currentTimestamp;
        }
      }
    }

    // Code for saving the image locally if no network connection is available
    // static Future<void> saveImageLocally(CameraController controller) async {
    //   if (isCapturing) return; // Exit if a capture is already in progress
    //
    //   isCapturing = true;
    //   try {
    //     final XFile file = await controller.takePicture();
    //     final Directory? directory = await getExternalStorageDirectory();
    //
    //     final String filePath = '${directory?.path}/${DateTime.now().millisecondsSinceEpoch}.jpg';
    //
    //     await file.saveTo(filePath); // Saves the image captured by the camera to the specified path
    //     developer.log('Image saved to $filePath', name: 'camera.save');
    //   } catch (e) {
    //     developer.log('Error saving image locally: $e', name: 'camera.error');
    //   } finally {
    //     isCapturing = false; // Reset the flag after operation completes
    //   }
    // }
  }

