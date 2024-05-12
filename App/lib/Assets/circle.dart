import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_3d_controller/flutter_3d_controller.dart';
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
  bool _isPlaying = false;


  Future<void> UpdateAvatarAnimations() async {
    print('UpdateAvatarAnimations called with state: ${stateManager.currentState}');
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


  Future<void> playSound(States state) async {
    if (_isPlaying) {
      print('playSound attempt blocked: Audio is already playing for state: $state');
      return; // Block further execution if audio is already playing
    }

    _isPlaying = true; // Set the flag to true as soon as playback is attempted
    String audioPath = getAudioPathForState(state); // Determine the audio file based on state

    print('Attempting to play audio: $audioPath');
    try {
      await audioPlayer.play(AssetSource(audioPath)); // Await the completion of the audio playback
      print('Audio playing started successfully for: $audioPath');
    } catch (e) {
      print('Error loading or playing audio: $e'); // Handle potential errors during audio loading/playing
    } finally {
      // Set a delay after playback finishes before allowing further audio playback
      Future.delayed(const Duration(milliseconds: 100), () {
        _isPlaying = false;
        print('Audio player is now free. Is playing: $_isPlaying');
      });
    }
  }

  String getAudioPathForState(States state) {
    switch (state) {
      case States.intro: return "Intro.mp3";
      case States.mouthOpeningIntro: return "Mouth_Opening_Intro.mp3";
      case States.mouthOpeningExercise: return "Mouth_Opening_Exercise.mp3";
      case States.mallampatiIntro: return "Mallampati_Intro.mp3";
      case States.mallampatiExercise: return "Mallampati_Exercise.mp3";
      case States.neckMovementIntro: return "Neck_Movement_Intro.mp3";
      case States.neckMovementExercise: return "Neck_Movement_Exercise.mp3";
      case States.thanks: return "Final.mp3";
      case States.oopsEyeHeight: return "Wrong_eye_height.mp3";
      case States.oopsFaceParallel: return "Wrong_tilt.mp3";
      case States.oopsNoFace: return "Wrong_face.mp3";
      case States.oopsBrightness: return "Wrong_brightness.mp3";
      default: return "How.mp3"; // Handle unexpected states
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
