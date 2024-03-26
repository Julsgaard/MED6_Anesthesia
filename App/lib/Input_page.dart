import 'package:camera/camera.dart';
import "package:flutter/material.dart";
import 'package:auto_size_text/auto_size_text.dart';
import 'camera_recording.dart';
import '../assets/circle.dart';

class InputPage extends StatelessWidget {
  final CameraDescription camera;
  const InputPage({
    super.key,
    required this.camera,
    re
  });


  @override
  Widget build(BuildContext context) {
    double mWidth= MediaQuery.of(context).size.width;
    double mHeight= MediaQuery.of(context).size.height;
    double circleHeight = (mHeight/5)*2;
    double textWidth = ((mWidth/8)*6);
    double textHeight = (mHeight/5)*3;
    double buttonPosW = (mWidth/3);
    double buttonPosH = (mHeight/10);
    return Material(
      child: Container(
        clipBehavior: Clip.antiAlias,
        decoration: const BoxDecoration(color: Color(0xFFEBEEF3)),
        child: Stack(
          children: [
            Circle(mWidth: mWidth, circleHeight: circleHeight,),
            Positioned(
              left: (mWidth/8),
              top: circleHeight/2 + 20,
              child: SizedBox(
                width: textWidth,
                height: textHeight,
                child: const AutoSizeText(
                  overflow: TextOverflow.fade,
                  softWrap: true,
                  minFontSize: 20,
                  'On this page you shall fill out some information about your medical state and history',
                  style: TextStyle(
                    color: Color(0xFF143868),
                    fontSize: 24,
                    fontFamily: 'Inter',
                    fontWeight: FontWeight.w400,
                    height: 0,
                  ),
                ),
              ),
            ),
            Positioned(
              left: buttonPosW,
              top: mHeight- buttonPosH,
              child: TextButton(
                style: ButtonStyle(
                    backgroundColor: MaterialStateProperty.all<Color>(const Color(0xFF153867))
                ),
                child: const Text(
                  'I have filled out \neverything proceed',
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
                  Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(builder: (context) => CameraRecording(title: 'Flutter Demo Home Page',
                          camera: camera))
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