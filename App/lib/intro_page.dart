import "package:flutter/material.dart";

class intro_page extends StatelessWidget {
  const intro_page({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        width: 360,
        height: 800,
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(color: Color(0xFFEBEEF3)),
        child: Stack(
          children: [
            Positioned(
              left: -73,
              top: -190,
              child: Container(
                width: 506,
                height: 392,
                decoration: ShapeDecoration(
                  gradient: LinearGradient(
                    begin: Alignment(0.00, -1.00),
                    end: Alignment(0, 1),
                    colors: [Color(0xFF153867), Color(0xFF38577F), Color(0xFF748EA8)],
                  ),
                  shape: OvalBorder(),
                ),
              ),
            ),
            Positioned(
              left: 39,
              top: 220,
              child: SizedBox(
                width: 282,
                height: 247,
                child: Text(
                  'Hello, to access if you can undergo a standard anesthesia procedure the doctor has ordered a review of your mouth and neck. Therefore we ask you to go through this online video consultation, where you will record yourself as guided by the video. This video recording will then be accessed by an AI, to determine if you can undergo standard procedure, or you need to see a real doctor',
                  style: TextStyle(
                    color: Color(0xFF143868),
                    fontSize: 16,
                    fontFamily: 'Inter',
                    fontWeight: FontWeight.w400,
                    height: 0,
                  ),
                ),
              ),
            ),
            Positioned(
              left: 60,
              top: 627,
              child: Container(
                width: 233,
                height: 75,
                decoration: ShapeDecoration(
                  color: Color(0xFF153867),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(51),
                  ),
                ),
              ),
            ),
            Positioned(
              left: 69,
              top: 627,
              child: SizedBox(
                width: 215,
                height: 75,
                child: Text(
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
              ),
            ),
          ],
        ),
      ),
    );
  }
}

