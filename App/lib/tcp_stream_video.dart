import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'dart:developer' as developer; // Import for logging
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image/image.dart' as imglib;
import 'image_utils.dart';
import 'package:camera_android_camerax/camera_android_camerax.dart';

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
  int _imagesCaptured = 0;
  int _lastLogTimestamp = DateTime.now().millisecondsSinceEpoch;
  bool _isStreaming = false;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.frontCamera,
      ResolutionPreset.medium,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.nv21
    );
    _controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
    });
  }

  void startStreaming({int frameIntervalMs = 50}) async {
    // 50 corresponds to approximately 20 frames per second, test other values as needed
    setState(() {
      _isStreaming = true;
    });
    socket = await Socket.connect('192.168.86.69', 5000);

    int lastTimestamp = DateTime.now().millisecondsSinceEpoch;

    // Here we assume that your CameraController has been properly initialized.
    String imageFormat = _controller.imageFormatGroup.toString();
    developer.log('Camera image format: $imageFormat', name: 'camera.info');

    _controller.startImageStream((CameraImage image) async {
      if (_isStreaming) {
        int currentTimestamp = DateTime.now().millisecondsSinceEpoch;
        if (currentTimestamp - lastTimestamp >= frameIntervalMs) {
          lastTimestamp = currentTimestamp;

          // Assuming the image is in NV21 format or similar, consisting of Y plane followed by UV plane
          final Uint8List yPlane = image.planes[0].bytes; // Y plane
          final Uint8List uvPlane = image.planes[1].bytes; // UV plane (assuming NV21 format or similar)
          final int ySize = yPlane.length;
          final int uvSize = uvPlane.length;
          final int totalSize = ySize + uvSize;

          // Log the image format, size, and resolution
          final int width = image.width;
          final int height = image.height;
          developer.log('Image format: $imageFormat, Size: $totalSize bytes, Resolution: ${width}x${height}', name: 'camera.info');

          if (totalSize > 0) {
            // Prepare and send the total size of the concatenated image data
            final ByteData byteData = ByteData(4);
            byteData.setUint32(0, totalSize, Endian.big);
            final Uint8List sizeHeader = byteData.buffer.asUint8List();

            socket.add(sizeHeader); // Send the total size of the concatenated image data

            // Concatenate Y and UV data for NV21 format and send
            final Uint8List nv21Data = Uint8List.fromList(yPlane + uvPlane);
            socket.add(nv21Data); // Send the actual concatenated image bytes

            // Logging the number of images captured every second
            if (currentTimestamp - _lastLogTimestamp >= 1000) {
              developer.log('Images captured in last second: $_imagesCaptured', name: 'camera.capture');
              _imagesCaptured = 0;
              _lastLogTimestamp = currentTimestamp;
            }
          }
        }
      }
    });
  }




  // Future<void> startStreaming() async {
  //   socket = await Socket.connect('192.168.8.150', 5000); // Use your server IP and port
  //   _isStreaming = true;
  //   _controller.startImageStream((CameraImage cameraImage) async {
  //     if (_isStreaming) {
  //       // Convert the CameraImage to an RGB image
  //       final imglib.Image rgbImage = ImageUtils.convertCameraImage(cameraImage);
  //
  //       // Convert the image to a byte format (e.g., PNG) before sending
  //       List<int> imageBytes = imglib.encodePng(rgbImage);
  //
  //
  //       // Send the image bytes over TCP
  //       socket.add(Uint8List.fromList(imageBytes));
  //     }
  //   });
  // }

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

  //TODO Det her resize/compression code bliver ikk brugt endnu men man kan måske give det et forsøg hvis vi har lyst
  static Future<XFile> resizeImage(XFile file) async {
    // Temporary file path for the compressed file
    final tempDir = await getTemporaryDirectory();
    final targetPath = '${tempDir.path}/${DateTime
        .now()
        .millisecondsSinceEpoch}.jpg';

    // Resize the image to 300x300 and reduce the quality
    final compressedFile = await FlutterImageCompress.compressAndGetFile(
      file.path,
      targetPath,
      quality: 50,
      minWidth: 500,
      minHeight: 500,
    );

    if (compressedFile == null) {
      // If the compression is not successful, return the original file
      return file;
    } else {
      // Return the compressed file as XFile
      return XFile(compressedFile.path);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
