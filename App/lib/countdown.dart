import 'dart:async';
import 'package:flutter/material.dart';

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

  void startTimer() {
    const oneSecond = Duration(seconds: 1);
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
    return Scaffold(
      backgroundColor: Color(0xFFEBEEF3),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            _isCountingDown
                ? Text(
              'Time Remaining:',
              style: TextStyle(fontSize: 35, fontWeight: FontWeight.bold),
            )
                : Text(
              'Press the button to start',
              style: TextStyle(fontSize: 25, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            _isCountingDown
                ? Text(
              '$_secondsRemaining seconds',
              style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
            )
                : SizedBox(),
            SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(
                  width: 150, // Specify the width of the button
                  child: TextButton(
                    style: ButtonStyle(
                      backgroundColor: MaterialStateProperty.all<Color>(const Color(0xFF153867)),
                    ),
                    onPressed: () {
                      if (!_isCountingDown) {
                        setState(() {
                          _isCountingDown = true;
                        });
                        startTimer();
                      }
                    },
                    child: Text(
                      'Start \nCountdown',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontFamily: 'Inter',
                      ),
                    ),
                  ),
                ),
                SizedBox(width: 20), // Add space between the buttons
                SizedBox(
                  width: 150, // Specify the width of the button
                  child: TextButton(
                    style: ButtonStyle(
                      backgroundColor: MaterialStateProperty.all<Color>(const Color(0xFF153867)),
                    ),
                    onPressed: () {
                      // Navigate to a different page
                    },
                    child: Text(
                      'Go to \nPage',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontFamily: 'Inter',
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}