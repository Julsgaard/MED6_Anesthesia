import "package:flutter/material.dart";

class intro_page extends StatelessWidget {
  const intro_page({super.key});

  @override
  Widget build(BuildContext context) {
    double mWidth= MediaQuery.of(context).size.width;
    double mHeight= MediaQuery.of(context).size.height;
    double circleHeight = (mHeight/5)*2;
    double textWidth = ((mWidth/8)*6);
    double textHeight = (mHeight/5)*3;
    return Center(
      child: Container(
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(color: Color(0xFFEBEEF3)),
        child: Stack(
          children: [
            Positioned(
              left: -mWidth/20,
              top: -circleHeight/2,
              child: Container(
                width: mWidth + mWidth/10,
                height: circleHeight,
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
              left: (mWidth/8),
              top: circleHeight/2,
              child: SizedBox(
                width: textWidth,
                height: textHeight,
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

