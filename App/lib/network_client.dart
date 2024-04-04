import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:dart/main.dart';

class NetworkClient {
  Socket? _socket;

  // Singleton pattern to ensure only one instance is created
  static final NetworkClient _instance = NetworkClient._internal();
  factory NetworkClient() => _instance;
  NetworkClient._internal();

  Future<void> initConnection() async {
    try {
      _socket = await Socket.connect(GlobalVariables.ipAddress, GlobalVariables.port, timeout: Duration(seconds: 5));
      _socket?.listen(_onDataReceived,
          onError: _onError,
          onDone: _onDone,
          cancelOnError: false);
    } catch (e) {
      print('Could not connect to the server: $e');
      // Implement reconnection logic or error handling as needed
    }
  }

  void sendData(String data) {
    if (_socket != null) {
      _socket!.add(utf8.encode(data));
    }
  }

  // Method for sending binary data, e.g., compressed camera footage
  void sendBinaryData(Uint8List data) {
    _socket?.add(data);
  }

  void _onDataReceived(data) {
    // Handle data received from the server if needed
  }

  void _onError(error, StackTrace trace) {
    print('Error: $error');
    // Handle any error here
  }

  void _onDone() {
    print('Disconnected from the server.');
    // Handle disconnection here, possibly attempt to reconnect
  }

  void closeConnection() {
    _socket?.close();
  }
}
