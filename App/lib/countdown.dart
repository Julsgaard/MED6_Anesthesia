import 'dart:async';
import 'package:flutter/material.dart';
import 'package:dart/Assets/circle.dart';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/services.dart';
import 'package:auto_size_text/auto_size_text.dart';
import 'camera_recording.dart';
import 'network_client.dart';

void main() {
  runApp(StartCountdown());
}

class StartCountdown extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.black),
        useMaterial3: true,
      ),
      home: CountdownScreen(),
    );
  }
}

class CountdownScreen extends StatefulWidget {
  @override
  _CountdownScreenState createState() => _CountdownScreenState();
}

class _CountdownScreenState extends State<CountdownScreen> {
  int _secondsRemaining = 10; // Initial countdown time in seconds
  late Timer _timer;

  bool _isCountingDown = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }


  void startTimer(int duration) {
    const oneSecond = Duration(seconds: 1);
    _secondsRemaining = duration;
    _timer = Timer.periodic(oneSecond, (timer) {
      setState(() {
        if (_secondsRemaining <= 0) {
          timer.cancel();
        } else {
          _secondsRemaining -= 1;
        }
      });
    });
  }


  @override
  Widget build(BuildContext context) {
    double mWidth = MediaQuery.of(context).size.width;
    double mHeight = MediaQuery.of(context).size.height;
    double circleHeight = (mHeight / 5) * 2;
    double cameraWidth = (mWidth / 7) * 6;
    double cameraHeight = (mHeight / 12) * 8;
    double buttonPosW = (mWidth / 7);
    double buttonPosH = (mHeight / 10);
    double buttonWidth = (mWidth / 4);
    double buttonHeight = (mHeight / 16);
    return Material(
        child: Stack(
            children: [
              Circle(mWidth: mWidth, circleHeight: circleHeight,),
              Positioned(
                left: (mWidth - cameraWidth) / 2,
                top: circleHeight / 2 + 10,
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
                ),
              ),
              Positioned(
                right: buttonPosW,
                top: mHeight - buttonPosH,
                child: TextButton(
                  style: ButtonStyle(
                    backgroundColor: MaterialStateProperty.all<Color>(const Color(0xFF153867)),
                    minimumSize: MaterialStateProperty.all(Size(buttonWidth, buttonHeight)),
                    maximumSize: MaterialStateProperty.all(Size(buttonWidth, buttonHeight)),
                  ),
                  onPressed: () {
                    // Start the countdown with the desired duration
                    startTimer(10); // Example: Start the countdown for 10 seconds
                  },
                  child: const Text(
                    'Continue \n anyway',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontFamily: 'Inter',
                      fontWeight: FontWeight.w400,
                      height: 0,
                    ),
                  ),
                ),
              ),
              Positioned(
                left: buttonPosW,
                top: mHeight - buttonPosH,
                child: TextButton(
                  style: ButtonStyle(
                    backgroundColor: MaterialStateProperty.all<Color>(
                        const Color(0xFF153867)),
                    minimumSize: MaterialStateProperty.all(
                        Size(buttonWidth, buttonHeight,)),
                    maximumSize: MaterialStateProperty.all(
                        Size(buttonWidth, buttonHeight,)),
                  ),
                  onPressed: () {

                  },
                  child: const Text(
                    'Repeat \ninstructions',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontFamily: 'Inter',
                      fontWeight: FontWeight.w400,
                      height: 0,
                    ),
                  ),
                ),
              ),
              Column(
                children: <Widget>[
                  SizedBox(height: 300,width: 400),
                  Text(
                    '$_secondsRemaining',
                    style: TextStyle(
                      fontSize: 225,
                      fontWeight: FontWeight.bold,
                      color: Colors.black.withOpacity(0.5), // Set text color with opacity
                    ),
                  ),
                ],
              )
    ]));
  }

}