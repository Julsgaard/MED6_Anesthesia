import 'package:camera/camera.dart';
import "package:flutter/material.dart";
import 'package:flutter/services.dart';
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
    double textHeight = (mHeight/12)*2;
    double weightInputHeight = (mHeight/15)*2;
    double buttonPosW = (mWidth/4);
    double buttonPosH = (mHeight/10);
    double buttonWidth = (mWidth/2);
    double buttonHeight = (mHeight/15);
    double gab = 20;
    String weight;
    String difficultyOfIntubation;

    return Material(
      child: Container(
        clipBehavior: Clip.antiAlias,
        decoration: const BoxDecoration(color: Color(0xFFEBEEF3)),
        child: Stack(
          children: [
            Circle(mWidth: mWidth, circleHeight: circleHeight,),
            Positioned(
              left: (mWidth/8),
              top: circleHeight/2 + gab,
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
            Positioned(
              top: (circleHeight/2) + (gab*2) + textHeight,
              left: mWidth/8,
              width: textWidth,
              height: weightInputHeight,
                child: TextField(
                    onChanged: (text) {
                      weight = text;
                    },
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: 'Enter Your weight in kg',
                    ),
                    keyboardType: TextInputType.number,
                    inputFormatters: <TextInputFormatter>[
                      FilteringTextInputFormatter.digitsOnly
                    ],
                  ),
                ),
            Positioned(
              left: (mWidth/8),
              top:(circleHeight/2) + (gab*3) + textHeight + weightInputHeight,
              child: DropdownMenu<String>(
                label: const Text("Do you have any previous difficulty with intubation?"),
                width: textWidth,
                dropdownMenuEntries: const [
                  DropdownMenuEntry( value: "No difficulty", label: "No difficulty",),
                  DropdownMenuEntry( value: "Definite difficulty",label:"Definite difficulty",),
                ],
                enableSearch: false,
                onSelected: (String? selectedValue) {
                  difficultyOfIntubation = selectedValue!;
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
                  //TODO: Send weight and difficulty of intibation to the server
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