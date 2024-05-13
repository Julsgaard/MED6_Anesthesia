import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_3d_controller/flutter_3d_controller.dart';
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
  final Flutter3DController animationController;
  const CameraRecording({
    Key? key,
    required this.title,
    required this.camera,
    required this.animationController,
  }) : super(key: key);

  @override
  _CameraRecordingState createState() => _CameraRecordingState();
}

class _CameraRecordingState extends State<CameraRecording> with WidgetsBindingObserver {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  late StreamSubscription<AccelerometerEvent> accelerometerSubscription;
  int _secondsRemaining = 10; // Initial value
  OverlayEntry? overlayEntry;
  final StateManager stateManager = GlobalVariables.stateManager;
  Timer? _checkForErrorStateTimer;
  bool _isFinalScreenOpen = false;


  @override
  void initState() {
    super.initState();
    bool showState = true; // Default is true, toggle this to show/hide the state display

    stateManager.addListener(_onStateChanged); // Listen to state changes
    _checkForErrorStateTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
      if (stateManager.currentState == States.mouthOpeningExercise ||
          stateManager.currentState == States.mallampatiExercise ||
          stateManager.currentState == States.neckMovementExercise ||
          stateManager.currentState == States.oopsEyeHeight ||
          stateManager.currentState == States.oopsFaceParallel ||
          stateManager.currentState == States.oopsNoFace ||
          stateManager.currentState == States.oopsBrightness) {
        _checkGlobalVariables();
      }
    });

    // Listener for accelerometer events
    accelerometerSubscription = accelerometerEvents.listen((AccelerometerEvent event) {
      // Assuming the phone is mostly upright, you can calculate the tilt
      // angle around the x-axis using the arctan of the y/z acceleration values.
      // This is a simplification and might need adjustment for your use case.

      // TODO All the state checks are basically just placed inside the accelerometer event listener, maybe change this to a separate function
      //print("Current state: ${stateManager.currentState}"); // Print the current state for debugging purposes
      GlobalVariables.tiltAngle = math.atan2(event.y, event.z) * 180 / math.pi;
    });
    SchedulerBinding.instance.addPostFrameCallback((timeStamp) {GlobalVariables.stateManager.notifyListeners();});

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

  void _checkGlobalVariables() {
    if (GlobalVariables.luxValue < 0) {
      GlobalVariables.overlayNumber = 1;
      stateManager.changeState(States.oopsBrightness);
    } else if (GlobalVariables.luxValue >= 300) {
      GlobalVariables.overlayNumber = 2;
      stateManager.changeState(States.oopsBrightness);
    } else if (GlobalVariables.eyeLevel == 0 &&
        (stateManager.currentState != States.mallampatiExercise &&
        stateManager.currentState != States.neckMovementExercise &&
        stateManager.previousState != States.neckMovementExercise &&
        stateManager.previousState != States.mallampatiExercise)) {
      GlobalVariables.overlayNumber = 3;
      stateManager.changeState(States.oopsNoFace);
    } else if (GlobalVariables.eyeLevel == 2 &&
        (stateManager.currentState != States.mallampatiExercise &&
            stateManager.currentState != States.neckMovementExercise &&
            stateManager.previousState != States.neckMovementExercise &&
            stateManager.previousState != States.mallampatiExercise)) {
      GlobalVariables.overlayNumber = 4;
      stateManager.changeState(States.oopsEyeHeight);
    } else if (GlobalVariables.eyeLevel == 3 &&
        (stateManager.currentState != States.mallampatiExercise &&
            stateManager.currentState != States.neckMovementExercise &&
            stateManager.previousState != States.neckMovementExercise &&
            stateManager.previousState != States.mallampatiExercise)) {
      GlobalVariables.overlayNumber = 5;
      stateManager.changeState(States.oopsEyeHeight);
    } else if (GlobalVariables.tiltAngle < 90-40) {
      GlobalVariables.overlayNumber = 6;
      stateManager.changeState(States.oopsFaceParallel);
    } else if (GlobalVariables.tiltAngle > 90+40) {
      GlobalVariables.overlayNumber = 7;
      stateManager.changeState(States.oopsFaceParallel);
    } else {
      // Default case if no other condition is met
      GlobalVariables.overlayNumber = 0;
      if (stateManager.currentState.index >= stateManager.errorStateIndex) {
        stateManager.changeState(stateManager.previousState); // Change state back to the previous state
      }
    }
  }


  @override
  void dispose() {
    //CameraServices.isStreaming = false; // Ensure the stream is turned off when the widget is disposed
    stateManager.removeListener(_onStateChanged); // Remove the listener
    accelerometerSubscription.cancel(); // Cancel the accelerometer subscription
    _controller.dispose(); // Dispose the controller
    WidgetsBinding.instance.removeObserver(this);
    stopTimer();
    super.dispose();
  }



  Timer? _timer;
  Timer? waitTimer;
  // create a cancelable operation
  int timerRuns = 0;
  Future<void> startTimer(List<int> duration, [ List<int> startAfterMilliseconds = const [0], List<bool> switchStateAfterwards = const [false] /*, bool countUp = false*/]) async{
    stopTimer();
    waitTimer = Timer(Duration(milliseconds: startAfterMilliseconds[timerRuns]), () {
      overlayEntry = OverlayEntry(builder: (context) {
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
      const oneSecond = Duration(seconds: 1);
      /*if(!countUp){*/
      _secondsRemaining = duration[timerRuns];
      _timer = Timer.periodic(oneSecond, (timer) {
        if (_secondsRemaining <= 0) {
          stopTimer();
          if (switchStateAfterwards[timerRuns] == true){
            timerRuns = 0;
            stateManager.nextState();
          }else {
            timerRuns++;
            startTimer(duration, startAfterMilliseconds, switchStateAfterwards);
          }
          return;
        } else {
          setState(() {
            _secondsRemaining -= 1;
            if (overlayEntry != null) {
              overlayEntry!.markNeedsBuild();
            }
          });
        }
      });
      /*}else{
        _secondsRemaining = 0;
        _timer = Timer.periodic(oneSecond, (timer) {
          if (_secondsRemaining >= duration) {
            timer.cancel();
            overlayEntry?.remove();
            overlayEntry = null;
          } else {
            setState(() {
              _secondsRemaining += 1;
              if (overlayEntry != null) {
                overlayEntry!.markNeedsBuild();
              }
            });
          }
        });
      }*/
    });
    
  }
  void stopTimer() {
    if(waitTimer != null){
      waitTimer!.cancel();
      waitTimer = null;
      overlayEntry?.remove();
      overlayEntry?.dispose();
      overlayEntry = null;
    }
    if (_timer != null) {
      overlayEntry?.remove();
      overlayEntry?.dispose();
      overlayEntry = null;
      _timer!.cancel();
      _timer = null;
    }
  }

// For handling state changes (mouth opening, mallampati, neck movement)
  _onStateChanged() {
    setState(() {
      //write a switch case for each state
      switch(stateManager.currentState){
        case States.mouthOpeningIntro:
         startTimer([3], [36250], [true]);
          break;
        case States.mouthOpeningExercise:
          startTimer([6,7], [3334, 5000], [false, true]);
          break;
        case States.mallampatiIntro:
          startTimer([3], [41250], [true]);
          break;
        case States.mallampatiExercise:
          startTimer([4], [12708], [true]);
          break;
        case States.neckMovementIntro:
          startTimer([3], [46000], [true]);
          break;
        case States.neckMovementExercise:
          startTimer([0], [47710], [true]);
          break;
        default:
          stopTimer();
          break;
      }
    });
  }



  // For the app to pause and resume streaming when it is in the background or foreground
  // @override
  // void didChangeAppLifecycleState(AppLifecycleState state) {
  //   super.didChangeAppLifecycleState(state);
  //   if (state == AppLifecycleState.resumed) {
  //     // Only restart streaming if it was previously active
  //     if (CameraServices.isStreaming) {
  //       CameraServices.streamCameraFootage(_controller, stateManager);
  //     }
  //   } else if (state == AppLifecycleState.paused) {
  //     CameraServices.isStreaming = false; // Stop streaming when the app is paused
  //   }
  // }

  @override
  Widget build(BuildContext context) {
    double mWidth= MediaQuery.of(context).size.width;
    double mHeight= MediaQuery.of(context).size.height;
    double circleHeight = (mHeight/5)*2;
    double cameraWidth = (mWidth/7)*6;
    double cameraHeight = (mHeight/12)*8;
    double buttonPosW = (mWidth/9);
    double buttonPosH = (mHeight/10);
    double buttonWidth = (mWidth/3);
    double buttonHeight = (mHeight/16);

    double mouthOverlayScale = 0.3; //Juster den her for at gøre mouthoverlay større/mindre, skal være mellem 0-1 (Sat til 0.3 der hvor vi samlede data til mallampati AI)

    if (stateManager.currentState.index == 8 && !_isFinalScreenOpen) { // Thank you page
      stopTimer();
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => InfoPage(
            camera: widget.camera,
            infoText: 'Thanks for participating!',
            animationController: widget.animationController,
            showContinueButton: false,
          )),
        );
      });
      _isFinalScreenOpen = true;
    }
    return Material(
      child: Stack(
        children: [
          Circle(key: GlobalVariables.circleKey, mWidth: mWidth, circleHeight: circleHeight,animationController: widget.animationController,),
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
                        Positioned.fill( // THIS IS WHERE THE CAMERA IS PLACED
                          child: AspectRatio(
                            aspectRatio: _controller.value.aspectRatio,
                            child: CameraPreview(_controller),
                          ),
                        ),
                        // Add a recording icon to indicate for the user that the camera is recording
                        if (stateManager.currentState == States.mouthOpeningExercise ||
                            stateManager.currentState == States.mallampatiExercise ||
                            stateManager.currentState == States.neckMovementExercise)
                          Positioned(
                            top: -10,
                            left: 4,
                            child: Image.asset('assets/recording_video_icon.png', width: 50, height: 50)
                          ),

                        if (stateManager.currentState == States.mallampatiIntro || stateManager.currentState == States.mallampatiExercise)
                          Positioned.fill( //THIS WHERE THE MOUTH IMAGE IS PLACED
                            child: Transform.translate(
                              offset: Offset(0, 30), // Adjust the offset to move the image
                              child: Transform.scale(
                                scale: mouthOverlayScale,
                                child: Image.asset(
                                  'assets/mallampatti_1.png',
                                  fit: BoxFit.contain,
                                ),
                              ),
                            ),
                          ),
                        if (GlobalVariables.showState) // Conditional display of current state
                          Positioned(
                            left: buttonPosW - 35,
                            bottom: buttonPosH + 400, // Adjust the position as needed
                            child: Text(
                              'Current State: ${stateManager.currentState.toString().split('.').last}',
                              style: const TextStyle(
                                color: Colors.blue,
                                fontSize: 18,
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
            Align(
                alignment: Alignment.center,
                child: Padding(
                  padding: EdgeInsets.only(top: 500), // Sets the top offset
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
                  fontSize: 14,
                  fontFamily: 'Inter',
                  fontWeight: FontWeight.w400,
                  height: 0,
                ),
              ),
              onPressed: (){
                stateManager.nextState();
                /*// Get the current state as an integer
                int currentStateInt = stateManager.currentState.index;
                //print('BUTTON PRESSED and Current state index: $currentStateInt');
                // +1 to the current state
                currentStateInt++;

                // If the incremented state exceeds the maximum, reset it to the first state to prevent an error
                if (currentStateInt >= States.values.length) {
                  int temp = States.values.length;
                  currentStateInt = 0;
                  //developer.log("Whoops, state index went over $temp");
                }

                // Convert the incremented integer back to a state
                States nextState = States.values[currentStateInt];

                // Change to the next state
                stateManager.changeState(nextState);

                //Stops countdown timer if any are running
                //stopTimer();
*/
              },
            ),
          ),

          Positioned(
            left: buttonPosW,
            top: mHeight- buttonPosH,
            child: TextButton(
              style: ButtonStyle(
                backgroundColor: MaterialStateProperty.all<Color>(
                  stateManager.currentState == States.mouthOpeningExercise || stateManager.currentState == States.mallampatiExercise || stateManager.currentState == States.neckMovementExercise ?
                  const Color(0xFF153867) : const Color(0xFFAAB4BE),
                ),

                minimumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
                maximumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
              ),
              child: const Text(
                'Repeat \ninstructions',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontFamily: 'Inter',
                  fontWeight: FontWeight.w400,
                  height: 0,
                ),
              ),
              onPressed: (){
                if (stateManager.currentState == States.mouthOpeningExercise || stateManager.currentState == States.mallampatiExercise || stateManager.currentState == States.neckMovementExercise) {
                    int currentStateInt = stateManager.currentState.index;
                    currentStateInt--;
                    States state = States.values[currentStateInt];
                    stateManager.changeState(state);
                  }

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