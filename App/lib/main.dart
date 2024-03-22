import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  final frontCamera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
  );
  runApp(MyApp(frontCamera: frontCamera));
}

class MyApp extends StatelessWidget {
  final CameraDescription frontCamera;

  const MyApp({Key? key, required this.frontCamera}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Video Streaming')),
        body: MyHomePage(frontCamera: frontCamera),
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  final CameraDescription frontCamera;

  const MyHomePage({Key? key, required this.frontCamera}) : super(key: key);

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  late CameraController _controller;
  late Socket socket;
  bool _isStreaming = false;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.frontCamera,
      ResolutionPreset.medium,
    );
    _controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
    });
  }

  void startStreaming() async {
    setState(() {
      _isStreaming = true;
    });
    socket = await Socket.connect('192.168.50.141', 5000);
    _controller.startImageStream((CameraImage image) async {
      if (_isStreaming) {
        // Simplified: Just send the first plane's data for now
        final Uint8List? imageData = image.planes.first.bytes;

        // Use null-aware operators to handle potential nulls
        final int imageSize = imageData?.length ?? 0;  // Provide a fallback value of 0

        if (imageData != null && imageSize > 0) {  // Check that imageData is not null and has size
          // Mock size sending (assuming the size can fit in 4 bytes)
          final ByteData byteData = ByteData(4);
          byteData.setUint32(0, imageSize, Endian.big);
          final Uint8List sizeHeader = byteData.buffer.asUint8List();

          socket.add(sizeHeader);
          socket.add(imageData);  // imageData is guaranteed not to be null here
        }
      }
    });
  }



  void stopStreaming() {
    setState(() {
      _isStreaming = false;
    });
    _controller.stopImageStream();
    socket.close();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          _controller.value.isInitialized
              ? AspectRatio(
            aspectRatio: _controller.value.aspectRatio,
            child: CameraPreview(_controller),
          )
              : Container(),
          ElevatedButton(
            onPressed: _isStreaming ? stopStreaming : startStreaming,
            child: Text(_isStreaming ? 'Stop Streaming' : 'Start Streaming'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
