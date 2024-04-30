import 'package:flutter/material.dart';
import 'package:flutter_3d_controller/flutter_3d_controller.dart';
class Circle extends StatelessWidget {

  const Circle({
    super.key,
    required this.mWidth,
    required this.circleHeight,
    required this.animationController
  });
  final double mWidth;
  final double circleHeight;
  final Flutter3DController animationController;

  @override
  Widget build(BuildContext context) {

    return Positioned(
      left: -mWidth/20,
      top: -circleHeight/2,
      child: Container(
        width: mWidth + mWidth/10,
        height: circleHeight,
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
          height: circleHeight/2 - 20,
          child: Flutter3DViewer(
            progressBarColor: Colors.transparent,
            controller: animationController,
            src: 'assets/business_man.glb',
          ),
        ),

      ),
    );
  }
}
