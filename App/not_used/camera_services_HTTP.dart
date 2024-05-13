import 'dart:async';
import 'dart:convert';
import 'package:camera/camera.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import '../lib/main.dart';
import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'dart:developer' as developer; // Import for logging

class CameraServices {

  static bool isStreaming = false; // Now a static variable, accessible from anywhere

  static Future<void> streamCameraFootage(CameraController controller) async {
    isStreaming = true; // Start streaming when this method is called
    while (isStreaming) { // Use the static variable here
      if (!controller.value.isInitialized || controller.value.isTakingPicture) {
        await Future.delayed(const Duration(milliseconds: 50));
        continue;
      }

      try {
        XFile file = await controller.takePicture();
        XFile resizedFile = await resizeImage(file);
        await sendImageToServer(
            resizedFile);
      } catch (e) {
        print(e); // Consider logging or handling the error differently
      }
    }
  }

  static Future<XFile> resizeImage(XFile file) async {
    // Temporary file path for the compressed file
    final tempDir = await getTemporaryDirectory();
    final targetPath = '${tempDir.path}/${DateTime
        .now()
        .millisecondsSinceEpoch}.jpg';

    // Resize the image to 300x300 and reduce the quality
    final compressedFile = await FlutterImageCompress.compressAndGetFile(
      file.path,
      targetPath,
      quality: 50,
      minWidth: 500,
      minHeight: 500,
    );

    if (compressedFile == null) {
      // If the compression is not successful, return the original file
      return file;
    } else {
      // Return the compressed file as XFile
      return XFile(compressedFile.path);
    }
  }

  static Future<void> sendImageToServer(XFile file) async {
    var request = http.MultipartRequest(
        'POST', Uri.parse(GlobalVariables.ipAddress));
    request.files.add(await http.MultipartFile.fromPath('picture', file.path));
    // Add the tilt angle as a field in the request
    request.fields['tiltAngle'] = GlobalVariables.tiltAngle.toString();

    var response = await request.send();
    response.stream.transform(utf8.decoder).listen((value) {
      print(value); // The string response from the server
    });
  }
}
