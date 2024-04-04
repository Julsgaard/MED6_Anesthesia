import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:dart/main.dart';

class NetworkClient {
  Socket? _socket; // Socket for the connection

  // Singleton pattern to ensure only one instance is created
  static final NetworkClient _instance = NetworkClient._internal();
  factory NetworkClient() => _instance;
  NetworkClient._internal();

  // Initialize the connection to the server
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
  }

  void _onError(error, StackTrace trace) {
    print('Error: $error');
  }

  void _onDone() {
    print('Disconnected from the server.');
  }

  void closeConnection() {
    _socket?.close();
  }
}
