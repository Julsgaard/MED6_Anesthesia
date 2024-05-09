import 'dart:async';
import 'dart:isolate';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_3d_controller/flutter_3d_controller.dart';

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
    States.blinking: "Blinking",
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

        // If the current animation is not the blinking animation, proceed to blink
        if (animationName != "Blinking") {
          // Wait for the current animation to finish
          await Future.delayed(Duration(milliseconds: widget.animationLength[animationName]!));

          // Loop to continuously play blinking animation until the state changes
          while (stateManager.currentState == originalState) {
            print("Inside while loop");
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



  @override
  void initState() {
    super.initState();
    stateManager.addListener(UpdateAvatarAnimations);
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
