import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'camera_services.dart';
import 'package:sensors/sensors.dart';
import 'dart:math' as math;
import 'package:dart/intro_page.dart';

List<CameraDescription>? cameras;
class GlobalVariables {
  // Static variable to hold the IP address
  static var ipAddress = "http://192.168.86.65:5000/upload";
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

class MyHomePage extends StatefulWidget {
  final CameraDescription camera;
  final String title;

  const MyHomePage({
    Key? key,
    required this.title,
    required this.camera,
  }) : super(key: key);

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> with WidgetsBindingObserver {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;

  // Variable to hold the tilt angle

  @override
  void initState() {
    super.initState();

    // Listener for accelerometer events
    accelerometerEvents.listen((AccelerometerEvent event) {
      // Assuming the phone is mostly upright, you can calculate the tilt
      // angle around the x-axis using the arctan of the y/z acceleration values.
      // This is a simplification and might need adjustment for your use case.
      setState(() {
        GlobalVariables.tiltAngle = math.atan2(event.y, event.z) * 180 / math.pi;
      });
    });

    WidgetsBinding.instance.addObserver(this);
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.max,
    );
    _initializeControllerFuture = _controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
      // Start streaming only if it is not already streaming
      if (!CameraServices.isStreaming) {
        CameraServices.streamCameraFootage(_controller);
      }
    });

  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    CameraServices.isStreaming = false; // Ensure the stream is turned off when the widget is disposed
    _controller.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      // Only restart streaming if it was previously active
      if (CameraServices.isStreaming) {
        CameraServices.streamCameraFootage(_controller);
      }
    } else if (state == AppLifecycleState.paused) {
      CameraServices.isStreaming = false; // Stop streaming when the app is paused
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Tilt Angle: ${GlobalVariables.tiltAngle} degrees'),
      ),
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            // The rest of your widget build method
            return Stack(
              children: <Widget>[
                Positioned.fill(
                  child: AspectRatio(
                    aspectRatio: _controller.value.aspectRatio,
                    child: CameraPreview(_controller),
                  ),
                ),
                Positioned(
                  bottom: 20,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: FloatingActionButton(
                      onPressed: () {
                        setState(() {
                          if (CameraServices.isStreaming) {
                            CameraServices.isStreaming = false; // Stops the stream
                          } else {
                            CameraServices.streamCameraFootage(_controller); // Starts the stream
                            CameraServices.isStreaming = true;
                          }
                        });
                      },
                      child: Icon(
                        CameraServices.isStreaming ? Icons.stop : Icons.videocam,
                      ),
                    ),
                  ),
                ),
              ],
            );
          } else {
            return Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}
