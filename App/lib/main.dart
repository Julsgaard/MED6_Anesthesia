import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'camera_services.dart'; // Assuming this is your updated CameraServices class with static isStreaming.

List<CameraDescription>? cameras;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  final frontCamera = cameras!.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
  );
  runApp(MyApp(camera: frontCamera));
}

class MyApp extends StatelessWidget {
  final CameraDescription camera;

  const MyApp({
    Key? key,
    required this.camera,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: MyHomePage(
        title: 'Flutter Demo Home Page',
        camera: camera,
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  final CameraDescription camera;
  final String title;

  const MyHomePage({
    Key? key,
    required this.title,
    required this.camera,
  }) : super(key: key);

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> with WidgetsBindingObserver {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.max,
    );
    _initializeControllerFuture = _controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
      // Start streaming only if it is not already streaming
      if (!CameraServices.isStreaming) {
        CameraServices.streamCameraFootage(_controller);
      }
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    CameraServices.isStreaming = false; // Ensure the stream is turned off when the widget is disposed
    _controller.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      // Only restart streaming if it was previously active
      if (CameraServices.isStreaming) {
        CameraServices.streamCameraFootage(_controller);
      }
    } else if (state == AppLifecycleState.paused) {
      CameraServices.isStreaming = false; // Stop streaming when the app is paused
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            // The rest of your widget build method
            return Stack(
              children: <Widget>[
                Positioned.fill(
                  child: AspectRatio(
                    aspectRatio: _controller.value.aspectRatio,
                    child: CameraPreview(_controller),
                  ),
                ),
                Positioned(
                  bottom: 20,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: FloatingActionButton(
                      onPressed: () {
                        setState(() {
                          if (CameraServices.isStreaming) {
                            CameraServices.isStreaming = false; // Stops the stream
                          } else {
                            CameraServices.streamCameraFootage(_controller); // Starts the stream
                            CameraServices.isStreaming = true;
                          }
                        });
                      },
                      child: Icon(
                        CameraServices.isStreaming ? Icons.stop : Icons.videocam,
                      ),
                    ),
                  ),
                ),
              ],
            );
          } else {
            return Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}
