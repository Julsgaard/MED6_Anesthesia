import 'dart:async';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

List<CameraDescription>? cameras;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: CameraApp(),
    );
  }
}

class CameraApp extends StatefulWidget {
  @override
  _CameraAppState createState() => _CameraAppState();
}

class _CameraAppState extends State<CameraApp> {
  CameraController? controller;
  String? videoPath;

  @override
  void initState() {
    super.initState();
    controller = CameraController(cameras![0], ResolutionPreset.medium);
    controller!.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
    });
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  Future<void> startVideoRecording() async {
    if (!controller!.value.isInitialized) {
      return;
    }
    if (controller!.value.isRecordingVideo) {
      // A recording is already started, do nothing.
      return;
    }

    try {
      await controller!.startVideoRecording();
    } catch (e) {
      print(e);
    }
  }

  Future<void> stopVideoRecording() async {
    if (!controller!.value.isRecordingVideo) {
      return;
    }

    try {
      final file = await controller!.stopVideoRecording();
      videoPath = file.path;
      if (videoPath != null) {
        sendVideoToServer(videoPath!);
      }
    } catch (e) {
      print(e);
    }
  }

  Future<void> sendVideoToServer(String path) async {
    try {
      File videoFile = File(path);
      String fileName = videoFile.path.split('/').last;
      FormData formData = FormData.fromMap({
        "file": await MultipartFile.fromFile(videoFile.path, filename: fileName),
      });

      var response = await Dio().post(
        'http://192.168.86.30:5000/upload',
        data: formData,
      );

      print("File upload response: $response");
    } catch (e) {
      print("Error sending file: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!controller!.value.isInitialized) {
      return Container();
    }
    return Scaffold(
      appBar: AppBar(
        title: Text('Send Video Stream'),
      ),
      body: Column(
        children: <Widget>[
          Expanded(
            child: Container(
              child: Padding(
                padding: const EdgeInsets.all(1.0),
                child: Center(
                  child: CameraPreview(controller!),
                ),
              ),
              decoration: BoxDecoration(
                color: Colors.black,
                border: Border.all(
                  color: controller != null && controller!.value.isRecordingVideo ? Colors.redAccent : Colors.grey,
                  width: 3.0,
                ),
              ),
            ),
          ),
          SizedBox(
            height: 10,
          ),
          FloatingActionButton(
            onPressed: () {
              if (controller != null) {
                if (controller!.value.isRecordingVideo) {
                  stopVideoRecording();
                } else {
                  startVideoRecording();
                }
              }
            },
            child: Icon(
              controller != null && controller!.value.isRecordingVideo ? Icons.stop : Icons.videocam,
            ),
          )
        ],
      ),
    );
  }
}
