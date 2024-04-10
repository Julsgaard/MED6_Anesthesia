import 'dart:async';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:camera_android_camerax/camera_android_camerax.dart';
import 'dart:developer' as developer; // Import for logging
import 'dart:typed_data';
import 'network_client.dart';
import 'state_manager.dart';


class CameraServices {

  static bool isStreaming = false; // Now a static variable, accessible from anywhere
  static int _imagesCaptured = 0;
  static int _lastLogTimestamp = DateTime.now().millisecondsSinceEpoch;

  static Future<void> streamCameraFootage(CameraController _controller, StateManager stateManager, {int frameIntervalMs = 50}) async {
    // 50 corresponds to approximately 20 frames per second, test other values as needed

    NetworkClient networkClient = NetworkClient();

    isStreaming = true;

    int lastTimestamp = DateTime.now().millisecondsSinceEpoch;

    // Here we assume that your CameraController has been properly initialized.
    String imageFormat = _controller.imageFormatGroup.toString();
    developer.log('Camera image format: $imageFormat', name: 'camera.info');

    _controller.startImageStream((CameraImage image) async { //TODO: Make ByteData to a function in network_client.dart
      if (isStreaming) {

        int currentTimestamp = DateTime.now().millisecondsSinceEpoch;
        if (currentTimestamp - lastTimestamp >= frameIntervalMs) {
          lastTimestamp = currentTimestamp;

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

          // Log the image format, size, and resolution
          final int width = image.width;
          final int height = image.height;
          //developer.log('Image format: $imageFormat, Size: $totalSize bytes, Resolution: ${width}x${height}', name: 'camera.info');

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
      }
    });
    }
  }

