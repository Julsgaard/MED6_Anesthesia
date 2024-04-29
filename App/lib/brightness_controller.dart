import 'dart:async';
import 'package:dart/main.dart';
import 'package:screen_brightness/screen_brightness.dart';
import 'dart:developer' as developer; // Import for logging
import 'package:light/light.dart';

class BrightnessController {
  final ScreenBrightness _screenBrightness = ScreenBrightness();
  final Light _light = Light();
  StreamSubscription? _lightSubscription;
  int _latestLuxValue = 0;

  void startListening() {
    _lightSubscription = _light.lightSensorStream.listen((luxValue) {
      // Do something with the lux value
      //developer.log('Lux value: $luxValue', name: 'camera.info');
      GlobalVariables.luxValue = luxValue;
      _latestLuxValue = luxValue;
    });
  }

  void stopListening() {
    _lightSubscription?.cancel();
  }

  int getLatestLuxValue() {
    return _latestLuxValue;
  }

  void setBrightnessToMax() {
    _screenBrightness.setScreenBrightness(1.0);
  }
}
