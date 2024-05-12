import 'dart:async';
import 'package:camera/camera.dart';
import 'package:dart/Assets/circle.dart';
import 'package:dart/state_manager.dart';
import 'package:flutter/material.dart';
import 'package:flutter_3d_controller/flutter_3d_controller.dart';
import 'package:sensors/sensors.dart';
import 'dart:math' as math;
import 'package:dart/info_page.dart';
import 'package:dart/camera_recording.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'network_client.dart';

List<CameraDescription>? cameras;
class GlobalVariables {
  static GlobalKey<CircleState> circleKey = GlobalKey();
  // Static variable to hold the IP address
  static var ipAddress = "No IP address set"; // SET IP IN APP
  static var port = 5000;
  // Static variable to hold the tilt angle
  static double tiltAngle = 0.0;
  static int luxValue = 0;
  static int eyeLevel = 0;
  static int overlayNumber = 0;
  static StateManager stateManager = StateManager();
  static bool showState = true;
  static Map<States,String> animationList= {
    States.intro: "Intro",
    States.mouthOpeningIntro: "MouthOpeningIntro",
    States.mouthOpeningExercise: "MouthOpeningExercise",
    States.mallampatiIntro: "MallampatiIntro",
    States.mallampatiExercise: "MallampatiExercise",
    States.neckMovementIntro: "NeckMovementIntro",
    States.neckMovementExercise: "HeadTiltExercise",
    States.thanks: "Final",
    States.oopsEyeHeight: "OopsEyeHeight",
    States.oopsFaceParallel: "OopsFaceParallel",
    States.oopsNoFace: "OopsNoFaceDetected",
    States.oopsBrightness: "OopsTooBright",

  };
  static Map<String,int> animationLength = {
    "Intro": 21250,
    "MouthOpeningIntro": 20125,
    "MouthOpeningExercise": 11459,
    "MallampatiIntro": 32667,
    "MallampatiExercise": 13750,
    "NeckMovementIntro": 40625,
    "HeadTiltExercise": 40709,
    "Final": 4125,
    "OopsEyeHeight": 10459,
    "OopsFaceParallel": 13834,
    "OopsNoFaceDetected":7167,
    "OopsTooBright": 5292,
  };
}


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  final frontCamera = cameras!.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
  );

  // Load the IP address from the shared preferences
  SharedPreferences prefs = await SharedPreferences.getInstance();
  String? ipAddress = prefs.getString('ipAddress');
  if (ipAddress != null) {
    GlobalVariables.ipAddress = ipAddress;
  }

  runApp(MyApp(camera: frontCamera));

  initNetworkClient();
  GlobalVariables.stateManager.changeState(States.intro);
}

// Initialize network client
Future<void> initNetworkClient() async {
  await NetworkClient().initConnection();
}


class MyApp extends StatelessWidget {
  final CameraDescription camera;
  Flutter3DController animationController = Flutter3DController();
  MyApp({
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
        infoText: 'Hello, to assess if you can undergo a standard anesthesia procedure I will now instruct you through 3 different exercises.\n\n'
            'I will start by explaining the exercise and throughout the exercise I will guide you.\n\n'
            'If any part of the exercise is performed incorrectly, I will assist you in correcting it.\n\n'
            'If you are ready, please proceed by clicking the button below, and filling in the required information.',
        animationController: animationController,
        showContinueButton: true,
      ),
    );
  }
}
