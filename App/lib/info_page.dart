import 'package:camera/camera.dart';
import 'package:dart/main.dart';
import 'package:dart/settings_page.dart';
import 'package:dart/state_manager.dart';
import "package:flutter/material.dart";
import 'package:auto_size_text/auto_size_text.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_3d_controller/flutter_3d_controller.dart';
import 'camera_recording.dart';
import 'package:dart/Assets/circle.dart';
import 'package:dart/Input_page.dart';
import '../state_manager.dart';

class InfoPage extends StatefulWidget {
  final CameraDescription camera;
  final String infoText;
  final Flutter3DController animationController;
  final bool showContinueButton;
  const InfoPage({
    super.key,
    required this.camera,
    required this.infoText,
    required this.animationController,
    required this.showContinueButton,
  });
  @override
  InfoStage createState() => InfoStage();
}

class InfoStage extends State<InfoPage>{

  final StateManager stateManager = GlobalVariables.stateManager;
  @override
  void initState() {
    super.initState();
    SchedulerBinding.instance.addPostFrameCallback((timeStamp) {GlobalVariables.stateManager.notifyListeners();});
  }


  @override
  Widget build(BuildContext context) {
    double mWidth= MediaQuery.of(context).size.width;
    double mHeight= MediaQuery.of(context).size.height;
    double circleHeight = (mHeight/5)*2;
    double textWidth = ((mWidth/8)*6);
    double textHeight = (mHeight/5)*3;
    double buttonPosW = (mWidth/4);
    double buttonPosH = (mHeight/10);
    double buttonWidth = (mWidth/2);
    double buttonHeight = (mHeight/15);
    return Material(
      child: Container(
        clipBehavior: Clip.antiAlias,
        decoration: const BoxDecoration(color: Color(0xFFEBEEF3)),
        child: Stack(
          children: [
            Circle(key: GlobalVariables.circleKey, mWidth: mWidth, circleHeight: circleHeight, animationController: widget.animationController),
            Positioned(
              left: (mWidth/8),
              top: circleHeight/2 + 20,
              child: SizedBox(
                width: textWidth,
                height: textHeight,
                child: AutoSizeText(
                  widget.infoText,
                  overflow: TextOverflow.fade,
                  softWrap: true,
                  minFontSize: 20,
                  style: const TextStyle(
                    color: Color(0xFF143868),
                    fontSize: 24,
                    fontFamily: 'Inter',
                    fontWeight: FontWeight.w400,
                    height: 0,
                  ),
                ),
              ),
            ),
            widget.showContinueButton
                ? Positioned(
              left: buttonPosW,
              top: mHeight- buttonPosH,
              child: TextButton(
                style: ButtonStyle(
                  backgroundColor: MaterialStateProperty.all<Color>(const Color(0xFF153867)),
                  minimumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
                  maximumSize: MaterialStateProperty.all(Size(buttonWidth,buttonHeight,)),
                ),
                child: const Text(
                  'I understand\nproceed',
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
                  stateManager.nextState();
                  Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(builder: (context) => InputPage(
                        camera: widget.camera, animationController: widget.animationController,))
                  );
                },
              ),
            )
                : Container(), // Invisible widget
            Positioned(
              right: 10,
              top: 30,
              child: IconButton(
                icon: const Icon(Icons.settings),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => SettingsPage()),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
