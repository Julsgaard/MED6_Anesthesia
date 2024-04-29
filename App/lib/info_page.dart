import 'package:camera/camera.dart';
import 'package:dart/settings_page.dart';
import "package:flutter/material.dart";
import 'package:auto_size_text/auto_size_text.dart';
import 'camera_recording.dart';
import '../assets/circle.dart';
import 'package:dart/Input_page.dart';

class InfoPage extends StatelessWidget {
  final CameraDescription camera;
  final String infoText;
  const InfoPage({
    super.key,
    required this.camera,
    required this.infoText
  });


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
            Circle(mWidth: mWidth, circleHeight: circleHeight,),
            Positioned(
              left: (mWidth/8),
              top: circleHeight/2 + 20,
              child: SizedBox(
                width: textWidth,
                height: textHeight,
                child: AutoSizeText(
                  infoText,
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
                  Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(builder: (context) => InputPage(
                          camera: camera))
                  );
                },
              ),
            ),
            Positioned(
              right: 10,
              top: 40,
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
