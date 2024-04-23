import 'dart:async';
import 'package:flutter/material.dart';
import 'package:dart/Assets/circle.dart';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/services.dart';
import 'package:auto_size_text/auto_size_text.dart';
import 'camera_recording.dart';
import 'network_client.dart';


int _secondsRemaining = 10;
class ShowCountdown {
  void startTimer(int duration) {
    late Timer _timer;
    const oneSecond = Duration(seconds: 1);
    _secondsRemaining = duration;
    _timer = Timer.periodic(oneSecond, (timer) {
      if (_secondsRemaining <= 0) {
        timer.cancel();
      } else {
        _secondsRemaining -= 1;
      }
    });
  }

  Widget showOverlay(BuildContext context) {
    return CountdownWidget();
  }
}

class CountdownWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Positioned(
      child: SizedBox(
        width: 400,
        height: 300,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '10101010',
              style: TextStyle(
                fontSize: 225,
              ),
            )
          ],
        ),
      ),
    );
  }
}