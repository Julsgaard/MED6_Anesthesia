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
    socket = await Socket.connect('192.168.8.150', 5000);

    _controller.startImageStream((CameraImage image) async {
      if (_isStreaming) {
        // Include resolution data
        final int width = image.width;
        final int height = image.height;

        final ByteData resolutionData = ByteData(8); // 4 bytes for width and 4 for height
        resolutionData.setUint32(0, width, Endian.big);
        resolutionData.setUint32(4, height, Endian.big);
        final Uint8List resolutionHeader = resolutionData.buffer.asUint8List();

        // Assuming we're still sending just the first plane's data for simplicity
        final Uint8List? imageData = image.planes.first.bytes;
        final int imageSize = imageData?.length ?? 0;

        final ByteData byteData = ByteData(4);
        byteData.setUint32(0, imageSize, Endian.big);
        final Uint8List sizeHeader = byteData.buffer.asUint8List();

        // Send resolution header, size header, then image data
        if (imageData != null && imageSize > 0) {
          socket.add(resolutionHeader);
          socket.add(sizeHeader);
          socket.add(imageData);
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
