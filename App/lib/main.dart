import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'camera_services.dart';

List<CameraDescription>? cameras;
//TODO: Camera looks a bit stretched
//TODO: Turn up the brightness of the camera like the camera app
//TODO: Framerate is better in camera app
//TODO: It bugs if the app has been running while the server is down and then the server is started again (a lot of old images are sent)
//TODO: Add comments
//TODO: Plz put todos where they belong in the code
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
  bool _isStreaming = false;

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
      _startStreaming();
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _stopStreaming();
    _controller.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      _controller.initialize().then((_) {
        if (!mounted) {
          return;
        }
        setState(() {});
        _startStreaming();
      });
    } else if (state == AppLifecycleState.paused) {
      _stopStreaming();
    }
  }

  void _startStreaming() {
    _isStreaming = true;
    CameraServices.streamCameraFootage(_controller, _isStreaming);
  }

  void _stopStreaming() {
    _isStreaming = false;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
      future: _initializeControllerFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          return AspectRatio(
            aspectRatio: _controller.value.isInitialized ? _controller.value.aspectRatio : 1,
            child: CameraPreview(_controller),
          );
        } else {
          return Center(child: CircularProgressIndicator());
        }
      },
    );
  }
}
