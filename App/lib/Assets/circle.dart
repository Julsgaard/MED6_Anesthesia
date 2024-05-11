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

  const Circle({
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


}
class CircleState extends State<Circle> with WidgetsBindingObserver{
  final StateManager stateManager = GlobalVariables.stateManager;
  late AudioPlayer audioPlayer;
  Future<void> UpdateAvatarAnimations() async {
    try {
      print("I update animations");
      // Fetch the list of available animations
      List<String> animations = await widget.animationController.getAvailableAnimations();

      if (animations.isNotEmpty) {
        print("These are the animations $animations");
        // Get the current state and save it to a local variable
        States originalState = stateManager.currentState;

        // Get the animation name for the original state
        String? animationName = GlobalVariables.animationList[originalState];
        print(animationName);
        widget.animationController.setCameraOrbit(0, 90, 100);
        // Play the animation for the original state
        if(animationName == null){
          widget.animationController.playAnimation(animationName: "Blinking");
          audioPlayer.stop();
        }else {
          widget.animationController.playAnimation(animationName: animationName);
          playSound(stateManager.currentState);
          Future.delayed(Duration(milliseconds: GlobalVariables.animationLength[animationName]!), () {
            widget.animationController.playAnimation(animationName: "Blinking");
          });
        }
      } else {
        // If no animations are available, retry after a short delay
        await Future.delayed(const Duration(milliseconds: 100));
        UpdateAvatarAnimations();
      }
    } catch (e) {
      // On error, retry after a short delay
      //print("Catch clause");
      await Future.delayed(const Duration(milliseconds: 100));
      UpdateAvatarAnimations();
    }

  }
  bool _isPlaying = false;
  int _howManyTimesHasSoundRun = 0;
  Future<void> playSound(States state) async {
    String audio;
    if (_isPlaying) return; // Exit if a sound is already being played
    _isPlaying = true;

    print("Sound has run $_howManyTimesHasSoundRun times");
    _howManyTimesHasSoundRun++;


    // Switch case to check for state 0-11 and set the corresponding audio path
    switch (state) {
      case States.intro:
        audio = "Intro.mp3";
        break;
      case States.mouthOpeningIntro:
        audio = "Mouth_Opening_Intro.mp3";
        break;
      case States.mouthOpeningExercise:
        audio = "Mouth_Opening_Exercise.mp3";
        break;
      case States.mallampatiIntro:
        audio = "Mallampati_Intro.mp3";
        break;
      case States.mallampatiExercise:
        audio = "Mallampati_Exercise.mp3";
        break;
      case States.neckMovementIntro:
        audio = "Neck_Movement_Intro.mp3";
        break;
      case States.neckMovementExercise:
        audio = "Neck_Movement_Exercise.mp3";
        break;
      case States.thanks:
        audio = "Final.mp3";
        break;
      case States.oopsEyeHeight:
        audio = "Wrong_eye_height.mp3";
        break;
      case States.oopsFaceParallel:
        audio = "Wrong_tilt.mp3";
        break;
      case States.oopsNoFace:
        audio = "Wrong_face.mp3";
        break;
      case States.oopsBrightness:
        audio = "Wrong_brightness.mp3";
        break;
      default:
        audio = "How";
        break;
    }
    audioPlayer.stop();
    try {
      print("Attempting to play audio: $audio");
      audioPlayer.play(AssetSource(audio));
    } catch (e) {
      print('Error loading audio: $e');
    }
    finally {
      _isPlaying = false; // Reset flag after playing
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
    print('CircleState disposed');
    stateManager.removeListener(UpdateAvatarAnimations);
    audioPlayer.dispose();
    super.dispose();
    //CameraServices.isStreaming = false; // Ensure the stream is turned off when the widget is disposed

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
