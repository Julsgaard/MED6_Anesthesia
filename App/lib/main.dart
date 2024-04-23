import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:sensors/sensors.dart';
import 'dart:math' as math;
import 'package:dart/info_page.dart';
import 'package:dart/camera_recording.dart';
import 'network_client.dart';

List<CameraDescription>? cameras;
class GlobalVariables {
  // Static variable to hold the IP address
  static var ipAddress = "192.168.86.89";
  static var port = 5000;
  // Static variable to hold the tilt angle
  static double tiltAngle = 0.0;
  static int luxValue = 0;
}


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  final frontCamera = cameras!.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
  );

  runApp(MyApp(camera: frontCamera));

  initNetworkClient();
}

// Initialize network client
Future<void> initNetworkClient() async {
  await NetworkClient().initConnection();
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
      home: InfoPage(
        camera: camera,
        infoText: 'Hello, to access if you can undergo a standard anesthesia procedure the doctor has ordered a review of your mouth and neck. Therefore we ask you to go through this online video consultation, where you will record yourself as guided by the video. This video recording will then be accessed by an AI, to determine if you can undergo standard procedure, or you need to see a real doctor',
      ),
    );
  }
}
