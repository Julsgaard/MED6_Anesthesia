import 'package:dart/main.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'network_client.dart';

class SettingsPage extends StatefulWidget {
  @override
  _SettingsPageState createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final TextEditingController _ipController = TextEditingController();
  String _currentIP = '';


  @override
  void initState() {
    super.initState();
    _loadIP();
  }

  _loadIP() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? ipAddress = prefs.getString('ipAddress');
    if (ipAddress != null) {
      setState(() {
        _currentIP = ipAddress;
        _ipController.text = ipAddress;
      });
    }
    else {
      setState(() {
        _currentIP = GlobalVariables.ipAddress;
      });
    }
  }

  _saveIP() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('ipAddress', _ipController.text);

    // Update the current IP state variable
    setState(() {
      _currentIP = _ipController.text;
    });

    // Update the global IP address
    GlobalVariables.ipAddress = _ipController.text;

    // Close the existing connection
    NetworkClient().closeConnection();

    // Initialize a new connection with the new IP address
    NetworkClient().initConnection();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Settings'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children: <Widget>[
            Text('Current IP: $_currentIP'), // Display the current IP
            TextField(
              controller: _ipController,
              decoration: InputDecoration(
                labelText: 'New IP Address',
              ),
            ),
            ElevatedButton(
              child: Text('Save'),
              onPressed: _saveIP,
            ),
          ],
        ),
      ),
    );
  }
}