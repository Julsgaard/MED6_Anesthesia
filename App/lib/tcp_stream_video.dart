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
    );
    _controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
    });
  }

  void startStreaming({int frameIntervalMs = 75}) async { // 50 svarer til cirka 15 billeder i sekundet, i kan teste andre værdier og kigge i loggen
    setState(() {
      _isStreaming = true;
    });
    socket = await Socket.connect('192.168.8.150', 5000);

    int lastTimestamp = DateTime.now().millisecondsSinceEpoch;

    _controller.startImageStream((CameraImage image) async {
      if (_isStreaming) {
        int currentTimestamp = DateTime.now().millisecondsSinceEpoch;
        if (currentTimestamp - lastTimestamp >= frameIntervalMs) {
          lastTimestamp = currentTimestamp;

          // Increment the counter since an image has been captured
          _imagesCaptured++;

          // final int width = image.width;
          // final int height = image.height;

          // final ByteData resolutionData = ByteData(8);
          // resolutionData.setUint32(0, width, Endian.big);
          // resolutionData.setUint32(4, height, Endian.big);
          // final Uint8List resolutionHeader = resolutionData.buffer.asUint8List();


          // Convert the CameraImage to an RGB image
          final imglib.Image rgbImage = ImageUtils.convertCameraImage(image);

          // Convert the image to a byte format (e.g., PNG) before sending
          List<int> imageBytes = imglib.encodePng(rgbImage);
          final int imageSize = imageBytes.length;

          // Convert imageSize to bytes and send it
          final ByteData byteData = ByteData(4);
          byteData.setUint32(0, imageSize, Endian.big);
          final Uint8List sizeHeader = byteData.buffer.asUint8List();


          // final Uint8List? imageData = image.planes.first.bytes;
          // final int imageSize = imageData?.length ?? 0;
          //
          // final ByteData byteData = ByteData(4);
          // byteData.setUint32(0, imageSize, Endian.big);
          // final Uint8List sizeHeader = byteData.buffer.asUint8List();

          if (imageSize > 0) {
            socket.add(sizeHeader);


            // Now send the image bytes
            socket.add(Uint8List.fromList(imageBytes));

            //socket.add(sizeHeader);

            // Send the image bytes over TCP
            //socket.add(Uint8List.fromList(imageBytes));

            // socket.add(resolutionHeader);
            // socket.add(sizeHeader);
            // socket.add(imageData);

            // Check if a second has passed since the last log
            if (currentTimestamp - _lastLogTimestamp >= 1000) {
              // Log the number of images captured in the last second
              developer.log('Images captured in last second: $_imagesCaptured', name: 'camera.capture');

              // Reset the counter and update the timestamp for the next log
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
