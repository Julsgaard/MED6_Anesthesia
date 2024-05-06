import 'dart:async';
import 'dart:math';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'camera_services_TCP.dart';
import 'package:sensors/sensors.dart';
import 'dart:math' as math;
import 'dart:developer' as developer; // Import for logging
import 'package:dart/info_page.dart';
import 'package:dart/Assets/circle.dart';
import 'main.dart';
import 'state_manager.dart';

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
  late Timer _timer;
  int _secondsRemaining = 10; // Initial value
  OverlayEntry? overlayEntry;
  final StateManager stateManager = StateManager();

  @override
  void initState() {
    super.initState();

    stateManager.addListener(_onStateChanged); // Listen to state changes

    // Listener for accelerometer events
    accelerometerSubscription = accelerometerEvents.listen((AccelerometerEvent event) {
      // Assuming the phone is mostly upright, you can calculate the tilt
      // angle around the x-axis using the arctan of the y/z acceleration values.
      // This is a simplification and might need adjustment for your use case.
      setState(() {
        GlobalVariables.tiltAngle = math.atan2(event.y, event.z) * 180 / math.pi;
      });
      if (GlobalVariables.luxValue <= 0 && GlobalVariables.overlayNumber == 0)
      {
        GlobalVariables.overlayNumber = 1;
      }
      if (GlobalVariables.luxValue >= 150 && GlobalVariables.overlayNumber == 0)
      {
        GlobalVariables.overlayNumber = 2;
      }
      if (GlobalVariables.luxValue >= 0 && GlobalVariables.luxValue <= 150 && GlobalVariables.overlayNumber == 1 || GlobalVariables.overlayNumber == 2)
      {
        GlobalVariables.overlayNumber = 0;
      }
      if (GlobalVariables.eyeLevel == 0 && GlobalVariables.overlayNumber == 0)
      {
        GlobalVariables.overlayNumber = 3;
      }
      if (GlobalVariables.eyeLevel == 2 && GlobalVariables.overlayNumber == 0)
      {
        GlobalVariables.overlayNumber = 4;
      }
      if (GlobalVariables.eyeLevel == 3  && GlobalVariables.overlayNumber == 0)
      {
        GlobalVariables.overlayNumber = 5;
      }
      if (GlobalVariables.eyeLevel == 1 && GlobalVariables.overlayNumber == 3 ||GlobalVariables.overlayNumber == 4||GlobalVariables.overlayNumber == 5)
      {
        GlobalVariables.overlayNumber = 0;
      }
      if (GlobalVariables.tiltAngle >= -90 && GlobalVariables.overlayNumber == 0)
      {
        GlobalVariables.overlayNumber = 6;
      }
      if (GlobalVariables.tiltAngle >= 90 && GlobalVariables.overlayNumber == 0)
      {
        GlobalVariables.overlayNumber = 7;
      }
      if (GlobalVariables.tiltAngle <= -90 && GlobalVariables.tiltAngle <= 90 && GlobalVariables.overlayNumber == 6 || GlobalVariables.overlayNumber == 7)
      {
        GlobalVariables.overlayNumber = 0;
      }
      if (GlobalVariables.luxValue >= 0 && GlobalVariables.luxValue <= 150 && GlobalVariables.eyeLevel == 1 && GlobalVariables.tiltAngle <= -90 && GlobalVariables.tiltAngle <= 90)
        {
          GlobalVariables.overlayNumber = 0;
        }
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
        CameraServices.streamCameraFootage(_controller, stateManager);
      }
    });
  }


  @override
  void dispose() {
    //CameraServices.isStreaming = false; // Ensure the stream is turned off when the widget is disposed
    stateManager.removeListener(_onStateChanged); // Remove the listener
    accelerometerSubscription.cancel(); // Cancel the accelerometer subscription
    _controller.dispose(); // Dispose the controller
    WidgetsBinding.instance.removeObserver(this);
    _timer.cancel();// Remove the observer
    super.dispose();
  }

  void startTimer(int duration) {
    const oneSecond = Duration(seconds: 1);
    _secondsRemaining = duration;
    _timer = Timer.periodic(oneSecond, (timer) {
      if (_secondsRemaining <= 0) {
        timer.cancel();
        overlayEntry?.remove();
        overlayEntry = null;
      } else {
        setState(() {
          _secondsRemaining -= 1;
          if (overlayEntry != null) {
            overlayEntry!.markNeedsBuild(); // Trigger rebuild of OverlayEntry
          }
        });
      }
    });
  }

  // For handling state changes (mouth opening, mallampati, neck movement)
  void _onStateChanged() {
    setState(() {

      //TODO: Start avatar animation for each state

      //TODO: Start countdown after avatar animation or button press

      if (stateManager.currentState == States.mouthOpening) {
        startTimer(10);
        developer.log('Mouth opening state');

      } else if (stateManager.currentState == States.mallampati) {
        startTimer(5);
        developer.log('Mallampati state');

      } else if (stateManager.currentState == States.neckMovement) {
        startTimer(20);
        developer.log('Neck movement state');

      }
      else {
        developer.log('Unknown state');
      }

    });
  }

  // For the app to pause and resume streaming when it is in the background or foreground
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      // Only restart streaming if it was previously active
      if (CameraServices.isStreaming) {
        CameraServices.streamCameraFootage(_controller, stateManager);
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

    double mouthOverlayScale = 0.3; //Juster den her for at gøre mouthoverlay større/mindre, skal være mellem 0-1 (Tror enten den skal være 0.4 eller 0.5)

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

                    //Sets the focus in the middle of the camera
                    // double fullWidth = MediaQuery.of(context).size.width;
                    // double cameraHeight = fullWidth * _controller.value.aspectRatio;
                    //
                    // double xp = fullWidth/2 ;
                    // double yp = cameraHeight/2;
                    //
                    // // Ensure the point coordinates are within the valid range
                    // Offset validPoint = Offset(
                    //   max(0.0, min(1.0, xp)),
                    //   max(0.0, min(1.0, yp)),
                    // );
                    // try {
                    //   _controller.setFocusPoint(validPoint);
                    // } catch (e) {
                    //   if (e is CameraException) {
                    //     developer.log('Failed to set focus point');
                    //   } else {
                    //     rethrow;
                    //   }
                    // }

                    return Stack(
                      children: <Widget>[
                        Positioned.fill( // THIS IS WHERE THE CAMERA IS PLACED
                          child: AspectRatio(
                            aspectRatio: _controller.value.aspectRatio,
                            child: CameraPreview(_controller),
                          ),
                        ),
                         Positioned.fill( //THIS WHERE THE MOUTH IMAGE IS PLACED
                           child: Transform.translate(
                             offset: Offset(0, 30), // Adjust the 100 to move it further down or less
                             child: Transform.scale(
                               scale: mouthOverlayScale,
                               child: Image.asset(
                                 'assets/mallampatti_1.png',
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
          ),
          if (GlobalVariables.overlayNumber > 0)
            Positioned(
                right: mWidth/2,
                top: 180,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Container(
                        padding: EdgeInsets.all(16.0),
                        decoration: BoxDecoration(
                          color: Colors.blue.withOpacity(0.5), // Adjust the opacity as needed
                          borderRadius: BorderRadius.circular(5.0),
                          border: Border.all(
                            color: Colors.black, // Border color
                            width: 2.0, // Optional: adds rounded corners
                          ),
                        ),
                      child: _getTextForCondition(),
                    ),
                  ],
                )),
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
                overlayEntry ??= OverlayEntry(builder: (context) {
                    return Positioned(
                      child: SizedBox(
                        width: 400,
                        height: 300,
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            DefaultTextStyle(style: TextStyle(
                              fontSize: 225,
                              fontWeight: FontWeight.bold,
                              color: Colors.black.withOpacity(0.5),),
                                child: Text('$_secondsRemaining',)
                            )
                          ],
                        ),
                      ),
                    );
                  });
                Overlay.of(context).insert(overlayEntry!);
                // Get the current state as an integer
                int currentStateInt = stateManager.currentState.index;

                // +1 to the current state
                currentStateInt++;

                // If the incremented state exceeds the maximum, reset it to the first state to prevent an error
                if (currentStateInt >= States.values.length) {
                  currentStateInt = 0;
                }

                // Convert the incremented integer back to a state
                States nextState = States.values[currentStateInt];

                // Change to the next state
                stateManager.changeState(nextState);

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
              onPressed: (){

              },
            ),
          ),

        ]
      )
    );
  }

  Widget _getTextForCondition () {
    switch (GlobalVariables.overlayNumber) {
      case 1:
        return _buildStyledText('Brightness too low!', FontWeight.bold, Colors.white, 30.0);
      case 2:
        return _buildStyledText('Brightness too high!', FontWeight.bold, Colors.white, 30.0);
      case 3:
        return _buildStyledText('No face detected', FontWeight.bold, Colors.white, 30.0);
      case 4:
        return _buildStyledText('Eyes too low', FontWeight.bold, Colors.white, 30.0);
      case 5:
        return _buildStyledText('Eyes too high', FontWeight.bold, Colors.white, 30.0);
      case 6:
        return _buildStyledText('You have tilted down', FontWeight.bold, Colors.white, 30.0);
      case 7:
        return _buildStyledText('You have tilted up', FontWeight.bold, Colors.white, 30.0);
      default:
        return Text('Detection error');
    }
  }

  Widget _buildStyledText(String text, FontWeight fontWeight, Color color, double textSize) {
    return Text(
      text,
      style: TextStyle(
        fontWeight: fontWeight,
        color: color,
      ),
    );
  }
}