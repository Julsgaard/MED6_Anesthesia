import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'dart:io';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';

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
      setState(() {
        // Update aspect ratio here
      });
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
        setState(() {
          // Update aspect ratio here
        });
        _startStreaming();
      });
    } else if (state == AppLifecycleState.paused) {
      _stopStreaming();
    }
  }

  void _startStreaming() {
    _isStreaming = true;
    _streamCameraFootage();
  }

  void _stopStreaming() {
    _isStreaming = false;
  }

  Future<void> _streamCameraFootage() async {
    while (_isStreaming) {
      if (!_controller.value.isInitialized || _controller.value.isTakingPicture) {
        await Future.delayed(const Duration(milliseconds: 50));
        continue;
      }

      try {
        XFile file = await _controller.takePicture();

        XFile resizedFile = await resizeImage(file);
        sendImageToServer(resizedFile);
      } catch (e) {
        print(e);
      }
    }
  }


  Future<XFile> resizeImage(XFile file) async {
    // Temporary file path for the compressed file
    final tempDir = await getTemporaryDirectory();
    final targetPath = '${tempDir.path}/${DateTime.now().millisecondsSinceEpoch}.jpg';

    // Resize the image to 300x300 and reduce the quality
    final compressedFile = await FlutterImageCompress.compressAndGetFile(
      file.path,
      targetPath,
      quality: 50,
      minWidth: 300,
      minHeight: 300,
    );

    if (compressedFile == null) {
      // If the compression is not successful, return the original file
      return file;
    } else {
      // Return the compressed file as XFile
      return XFile(compressedFile.path);
    }
  }


  void sendImageToServer(XFile file) async {
    var request = http.MultipartRequest('POST', Uri.parse('http://192.168.86.30:5000/upload'));
    request.files.add(await http.MultipartFile.fromPath('picture', file.path));

    var response = await request.send();
    response.stream.transform(utf8.decoder).listen((value) {
      print(value); // The string response from the server
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
      future: _initializeControllerFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          // Use aspect ratio from the controller
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
