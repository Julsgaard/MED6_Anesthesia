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
    States.mouthOpeningExercise: "MouthOpeningExercise",
    States.mouthOpeningIntro: "MouthOpeningIntro",
    States.mallampatiExercise: "MallampatiExercise",
    States.mallampatiIntro: "MallampatiIntro",
    States.neckMovementExercise: "HeadTiltExercise",
    States.neckMovementIntro: "NeckMovementIntro",
    States.intro: "Intro",
    States.thanks: "Final",
    States.oopsEyeHeight: "OopsEyeHeight",
    States.oopsFaceParallel: "OopsFaceParallel",
    States.blinking: "Blinking",
  };
  final Map<String,int> animationLength = {
    "MouthOpeningExercise": 11459,
    "MouthOpeningIntro": 20125,
    "MallampatiExercise": 13750,
    "MallampatiIntro": 36084,
    "HeadTiltExercise": 40709,
    "NeckMovementIntro": 40625,
    "Intro": 21250,
    "Final": 4125,
    "OopsEyeHeight": 10459,
    "OopsFaceParallel": 13834,
  };
}
class CircleState extends State<Circle> with WidgetsBindingObserver{
  final StateManager stateManager = GlobalVariables.stateManager;


  Future<void> UpdateAvatarAnimations() async{
    //print("I RUN ISOLATE");
    //await compute(waitForAnimations, widget.animationController);
    final perTimer = Timer.periodic(Duration(milliseconds: 100), (timer) async {
      List<String> animations = await widget.animationController.getAvailableAnimations();
      print("I WAIT FOR ANIMATIONS");
      if(animations.isNotEmpty) {
        print("IPLAYANIMATIONS");
        String animationName = widget.animationList[stateManager.currentState]!;
        widget.animationController.playAnimation(animationName: animationName);
        if(animationName != "Blinking") {
          Future.delayed(Duration(milliseconds: widget.animationLength[animationName]!), () {
            stateManager.changeState(States.blinking);
            print("IstartBlinking");
          });
        }else{
          widget.animationController.playAnimation(animationName: animationName);
        }
        timer.cancel();
      }
    });



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
