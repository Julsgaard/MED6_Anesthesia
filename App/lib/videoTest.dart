import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image/image.dart' as img;

Future<void> main() async {
  // Ensure that plugin services are initialized so that `availableCameras()`
  // can be called before `runApp()`
  WidgetsFlutterBinding.ensureInitialized();

  // Obtain a list of the available cameras on the device.
  final cameras = await availableCameras();

  // Get a specific camera from the list of available cameras.
  final firstCamera = cameras.first;

  runApp(
    MaterialApp(
      theme: ThemeData.dark(),
      home: TakePictureScreen(
        // Pass the appropriate camera to the TakePictureScreen widget.
        camera: firstCamera,
      ),
    ),
  );
}

class TakePictureScreen extends StatefulWidget {
  final CameraDescription camera;

  const TakePictureScreen({
    Key? key,
    required this.camera,
  }) : super(key: key);

  @override
  TakePictureScreenState createState() => TakePictureScreenState();
}

class TakePictureScreenState extends State<TakePictureScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  late Socket socket;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.medium,
    );
    _initializeControllerFuture = _controller.initialize();
    connectToServer();
  }

  void connectToServer() async {
    // Replace 'your_server_ip' with your server's IP address and '12345' with your designated port.
    socket = await Socket.connect('192.168.86.55', 5000);
    print('Connected to: ${socket.remoteAddress.address}:${socket.remotePort}');

    // Start streaming frames to the server
    startStreaming();
  }

  void startStreaming() async {
    await _initializeControllerFuture;
    const int frameInterval = 100; // milliseconds
    DateTime lastFrameTime = DateTime.now();

    _controller.startImageStream((CameraImage image) async {
      DateTime currentTime = DateTime.now();
      int timeSinceLastFrame = currentTime.difference(lastFrameTime).inMilliseconds;

      if (timeSinceLastFrame >= frameInterval) {
        // Update the last frame time
        lastFrameTime = currentTime;

        // Convert CameraImage to a byte array (e.g., JPEG)
        final Uint8List? bytes = await convertYUV420toImageColor(image);
        if (bytes != null) {
          socket.add(bytes);
        }
      }
    });
  }

  //TODO I think this conversion is causing the app side to lagg, maybe look for an alternative? Use a package/no conversion?
  Future<Uint8List?> convertYUV420toImageColor(CameraImage image) async {
    try {
      // The image captured is in YUV420 format
      final int width = image.width;
      final int height = image.height;
      // Updated for correct instantiation with named parameters
      final img.Image convertedImage = img.Image(width: width, height: height);

      // The first plane is the Y plane
      final Uint8List yPlane = image.planes[0].bytes;
      final int yRowStride = image.planes[0].bytesPerRow;

      // The second and third planes are for the U (Cb) and V (Cr) values respectively
      final Uint8List uPlane = image.planes[1].bytes;
      final Uint8List vPlane = image.planes[2].bytes;
      final int uvRowStride = image.planes[1].bytesPerRow;
      final int uvPixelStride = image.planes[1].bytesPerPixel!;

      // Convert YUV to RGB
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          final int uvIndex = uvPixelStride * (x / 2).floor() + uvRowStride * (y / 2).floor();
          final int index = y * yRowStride + x;
          final Y = yPlane[index];
          final U = uPlane[uvIndex];
          final V = vPlane[uvIndex];
          // Update this line in your convertYUV420toImageColor function
          convertedImage.setPixelRgba(x, y, _yuvToR(Y, U, V), _yuvToG(Y, U, V), _yuvToB(Y, U, V), 255); // Add 255 as the alpha value
        }
      }

      // Convert img.Image to Uint8List
      final convertedBytes = img.encodeJpg(convertedImage, quality: 20);
      return Uint8List.fromList(convertedBytes);
    } catch (e) {
      print("Error converting image: $e");
      return null;
    }
  }

  int _yuvToR(int y, int u, int v) {
    return (y + 1.402 * (v - 128)).round().clamp(0, 255);
  }

  int _yuvToG(int y, int u, int v) {
    return (y - 0.344136 * (u - 128) - 0.714136 * (v - 128)).round().clamp(0, 255);
  }

  int _yuvToB(int y, int u, int v) {
    return (y + 1.772 * (u - 128)).round().clamp(0, 255);
  }

  @override
  void dispose() {
    _controller.dispose();
    socket.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // You must wait until the controller is initialized before displaying the camera preview.
      // Use a FutureBuilder to display a loading spinner until the controller has finished initializing.
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            // If the Future is complete, display the preview.
            return CameraPreview(_controller);
          } else {
            // Otherwise, display a loading indicator.
            return Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}
