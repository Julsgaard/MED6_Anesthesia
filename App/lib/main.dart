import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'camera_services.dart';
import 'package:sensors/sensors.dart';
import 'dart:math' as math;
import 'package:dart/intro_page.dart';
import 'package:dart/camera_recording.dart';

List<CameraDescription>? cameras;
class GlobalVariables {
  // Static variable to hold the IP address
  static var ipAddress = "http://192.168.86.69:5000/upload";
  // Static variable to hold the tilt angle
  static double tiltAngle = 0.0;
}


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  final frontCamera = cameras!.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
  );
  runApp(MyApp(camera: frontCamera));
}


class MyApp extends StatelessWidget {
  final CameraDescription camera;

  const MyApp({
    Key? key,
    required this.camera,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: intro_page(
      ),
    );
  }
}
