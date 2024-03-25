import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'camera_services.dart';
import 'package:sensors/sensors.dart';
import 'dart:math' as math;
import 'package:dart/intro_page.dart';
import 'package:dart/Assets/circle.dart';
import 'main.dart';



class CameraRecording extends StatefulWidget {
  final CameraDescription camera;
  final String title;

  const CameraRecording({
    Key? key,
    required this.title,
    required this.camera,
  }) : super(key: key);

  @override
  _CameraRecordingState createState() => _CameraRecordingState();
}

class _CameraRecordingState extends State<CameraRecording> with WidgetsBindingObserver {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  late StreamSubscription<AccelerometerEvent> accelerometerSubscription;
  // Variable to hold the tilt angle

  @override
  void initState() {
    super.initState();

    // Listener for accelerometer events
    accelerometerSubscription = accelerometerEvents.listen((AccelerometerEvent event) {
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
    accelerometerSubscription.cancel();
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
    double mWidth= MediaQuery.of(context).size.width;
    double mHeight= MediaQuery.of(context).size.height;
    double circleHeight = (mHeight/5)*2;
    double cameraWidth = mWidth;
    double cameraHeight = (mHeight/5)*3;
    return Material(

      child: Stack(
        children: [
          Circle(mWidth: mWidth, circleHeight: circleHeight,),
          Positioned(
            left: 0,
            top: circleHeight/2 + 10,
            child: SizedBox(
              height: cameraHeight,
              width: cameraWidth,
              child: FutureBuilder<void>(
                future: _initializeControllerFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.done) {
                    return Stack(
                      children: <Widget>[
                        Positioned.fill(
                          child: AspectRatio(
                            aspectRatio: _controller.value.aspectRatio,
                            child: CameraPreview(_controller),
                          ),
                        ),
                        Positioned.fill( //THIS WHERE THE MOUTH IMAGE IS PLACED
                          child: Transform.translate(
                            offset: Offset(0, 30), // Adjust the 100 to move it further down or less
                            child: Transform.scale(
                              scale: 0.4, // Adjust the scale factor to make it bigger (greater than 1) or smaller (less than 1)
                              child: Image.asset(
                                'assets/mouth_overlay.png',
                                fit: BoxFit.contain,
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
            ),
          )
        ]
      )
    );
  }
}
