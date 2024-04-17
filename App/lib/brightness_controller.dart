import 'package:camera/camera.dart';
import 'package:screen_brightness/screen_brightness.dart';
import 'dart:developer' as developer; // Import for logging

class BrightnessController {
  final ScreenBrightness _screenBrightness = ScreenBrightness();

  void processImage(CameraImage image) {
    // Ensure this method can handle direct image processing calls
    double brightness = _calculateBrightness(image);
    _adjustScreenBrightness(brightness);
  }

  double _calculateBrightness(CameraImage image) { //TODO: Maybe calculate the brightness and use it for the avatar instead of adjusting the screen brightness
    int sumLuminance = 0;
    final int pixelCount = image.width * image.height;
    developer.log('Calculating brightness', name: 'BrightnessController');
    for (int i = 0; i < pixelCount; i++) {
      sumLuminance += image.planes[0].bytes[i];
    }
    double avgLuminance = sumLuminance / pixelCount;
    developer.log('Calculated brightness: $avgLuminance', name: 'BrightnessController');
    return avgLuminance / 255;  // Normalize the luminance
  }

  void _adjustScreenBrightness(double brightness) { //TODO: Maybe the brightness should always be on max
    double screenBrightness = brightness.clamp(0.0, 1.0);  // Ensure within range

    // Make the brightness darker the brighter the image
    screenBrightness = 1 - screenBrightness;

    developer.log('Adjusting screen brightness to: $screenBrightness', name: 'BrightnessController');
    _screenBrightness.setScreenBrightness(screenBrightness);
  }
}
