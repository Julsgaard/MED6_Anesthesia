import 'dart:async';
import 'dart:isolate';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_3d_controller/flutter_3d_controller.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:audioplayers/audioplayers.dart';

import '../main.dart';
import '../state_manager.dart';


class Circle extends StatefulWidget {

  Circle({
    super.key,
    required this.mWidth,
    required this.circleHeight,
    required this.animationController,
  });

  final double mWidth;
  final double circleHeight;
  final Flutter3DController animationController;

  @override
  CircleState createState() => CircleState();

  final Map<States,String> animationList= {
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
    States.oopsBrightness: "OopsBrightness",

  };
  final Map<String,int> animationLength = {
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
    "OopsBrightness": 5292,
  };
}
class CircleState extends State<Circle> with WidgetsBindingObserver{
  final StateManager stateManager = GlobalVariables.stateManager;
  late AudioPlayer audioPlayer;


  Future<void> UpdateAvatarAnimations() async {
    try {
      // Fetch the list of available animations
      List<String> animations = await widget.animationController.getAvailableAnimations();

      if (animations.isNotEmpty) {
        // Get the current state and save it to a local variable
        var originalState = stateManager.currentState;

        // Get the animation name for the original state
        String animationName = widget.animationList[originalState]!;
        widget.animationController.setCameraOrbit(0, 90, 100);
        // Play the animation for the original state
        widget.animationController.playAnimation(animationName: animationName);
        playSound(stateManager.currentState.index);
        // If the current animation is not the blinking animation, proceed to blink
        if (animationName != "Blinking") {
          // Wait for the current animation to finish
          await Future.delayed(Duration(milliseconds: widget.animationLength[animationName]!));

          // Loop to continuously play blinking animation until the state changes
          while (stateManager.currentState == originalState) {
            widget.animationController.setCameraOrbit(0, 90, 100);
            widget.animationController.playAnimation(animationName: "Blinking");
            await Future.delayed(Duration(milliseconds: 500));
          }
        }
      } else {
        // If no animations are available, retry after a short delay
        await Future.delayed(const Duration(milliseconds: 100));
        UpdateAvatarAnimations();
      }
    } catch (e) {
      // On error, retry after a short delay
      print("Catch clause");
      await Future.delayed(const Duration(milliseconds: 100));
      UpdateAvatarAnimations();
    }
  }

  Future<void> playSound(int state) async {
    String audio;

    // Switch case to check for state 0-11 and set the corresponding audio path
    switch (state) {
      case 0:
        audio = "Intro.mp3";
        break;
      case 1:
        audio = "Mouth_Opening_Intro.mp3";
        break;
      case 2:
        audio = "Mouth_Opening_Exercise.mp3";
        break;
      case 3:
        audio = "Mallampati_Intro.mp3";
        break;
      case 4:
        audio = "Mallampati_Exercise.mp3";
        break;
      case 5:
        audio = "Neck_Movement_Intro.mp3";
        break;
      case 6:
        audio = "Neck_Movement_Exercise.mp3";
        break;
      case 7:
        audio = "Final.mp3";
        break;
      case 8:
        audio = "Wrong_eye_height.mp3";
        break;
      case 9:
        audio = "Wrong_tilt.mp3";
        break;
      case 10:
        audio = "Wrong_face.mp3";
        break;
      case 11:
        audio = "Wrong_brightness.mp3";
        break;
      default:
        audio = "How";
    }
    if (audioPlayer.state == PlayerState.playing) {
      await audioPlayer.stop();
    }
    try {
      await audioPlayer.play(AssetSource(audio));
    } catch (e) {
      print('Error loading audio: $e');
    }
  }



  @override
  void initState() {
    super.initState();
    stateManager.addListener(UpdateAvatarAnimations);
    audioPlayer = AudioPlayer();
  }
  @override
  void dispose() {
    super.dispose();
    //CameraServices.isStreaming = false; // Ensure the stream is turned off when the widget is disposed
    stateManager.removeListener(UpdateAvatarAnimations);
  }

  @override
  Widget build(BuildContext context) {
    //SchedulerBinding.instance.addPostFrameCallback((timeStamp) {stateManager.changeState(States.intro);});
    return Positioned(
      left: -widget.mWidth/20,
      top: -widget.circleHeight/2,
      child: Container(
        width: widget.mWidth + widget.mWidth/10,
        height: widget.circleHeight,
        decoration: const ShapeDecoration(
        gradient: LinearGradient(
        begin: Alignment(0.00, -1.00),
        end: Alignment(0, 1),
        colors: [Color(0xFF153867), Color(0xFF38577F), Color(0xFF748EA8)],
        ),
        shape: OvalBorder(),
        ),
        alignment: const Alignment(0,1),
        child: SizedBox(
          height: widget.circleHeight/2 - 20,
          child: IgnorePointer(
            child: Flutter3DViewer(
              controller: widget.animationController,
              src: "assets/AppAvatar.glb",
            ),
          )
        ),
      ),
    );
  }
}
