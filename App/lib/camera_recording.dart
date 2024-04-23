import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'camera_services_TCP.dart';
import 'package:sensors/sensors.dart';
import 'dart:math' as math;
import 'package:dart/info_page.dart';
import 'package:dart/Assets/circle.dart';
import 'countdown.dart';
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
      ResolutionPreset.medium,
      enableAudio: false,
        imageFormatGroup: ImageFormatGroup.nv21
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
    double cameraWidth = (mWidth/7)*6;
    double cameraHeight = (mHeight/12)*8;
    double buttonPosW = (mWidth/7);
    double buttonPosH = (mHeight/10);
    double buttonWidth = (mWidth/4);
    double buttonHeight = (mHeight/16);
    return Material(

      child: Stack(
        children: [
          Circle(mWidth: mWidth, circleHeight: circleHeight,),
          Positioned(
            left: (mWidth - cameraWidth)/2,
            top: circleHeight/2 + 10,
            child: Container(
              height: cameraHeight,
              width: cameraWidth,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(10),
                    topRight: Radius.circular(10),
                    bottomLeft: Radius.circular(10),
                    bottomRight: Radius.circular(10)
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.5),
                    spreadRadius: 5,
                    blurRadius: 7,
                    offset: Offset(0, 3), // changes position of shadow
                  ),
                ],
              ),
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
                        // Positioned.fill( //THIS WHERE THE MOUTH IMAGE IS PLACED
                        //   child: Transform.translate(
                        //     offset: Offset(0, 30), // Adjust the 100 to move it further down or less
                        //     child: Transform.scale(
                        //       scale: 0.4, // Adjust the scale factor to make it bigger (greater than 1) or smaller (less than 1)
                        //       child: Image.asset(
                        //         'assets/mouth_overlay.png',
                        //         fit: BoxFit.contain,
                        //       ),
                        //     ),
                        //   ),
                        // ),
                      ],
                    );
                  } else {
                    return Center(child: CircularProgressIndicator());
                  }
                },
              ),
            ),
          ),
          Positioned(
            right: buttonPosW,
            top: mHeight- buttonPosH,
            child: TextButton(
              style: ButtonStyle(
                backgroundColor: MaterialStateProperty.all<Color>(const Color(0xFF153867)),
                minimumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
                maximumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
              ),
              child: const Text(
                'Continue \n anyway',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontFamily: 'Inter',
                  fontWeight: FontWeight.w400,
                  height: 0,
                ),
              ),
              onPressed: (){

              },
            ),
          ),
          Positioned(
            left: buttonPosW,
            top: mHeight- buttonPosH,
            child: TextButton(
              style: ButtonStyle(
                backgroundColor: MaterialStateProperty.all<Color>(const Color(0xFF153867)),
                minimumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
                maximumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
              ),
              child: const Text(
                'Repeat \ninstructions',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontFamily: 'Inter',
                  fontWeight: FontWeight.w400,
                  height: 0,
                ),
              ),
              onPressed: (){MaterialPageRoute(builder: (context) => CountdownWidget());

              },
            ),
          ),

        ]
      )
    );
  }
}
