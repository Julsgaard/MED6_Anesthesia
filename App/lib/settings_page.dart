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
  final TextEditingController _portController = TextEditingController();
  String _currentIP = '';
  int _currentPort = 0;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  _loadSettings() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? ipAddress = prefs.getString('ipAddress');
    int? port = prefs.getInt('port');
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
    if (port != null) {
      setState(() {
        _currentPort = port;
        _portController.text = port.toString();
      });
    }
    else {
      setState(() {
        _currentPort = GlobalVariables.port; // Default port
        _portController.text = GlobalVariables.port.toString(); // Default port as a string
      });
    }
  }

  _saveSettings() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('ipAddress', _ipController.text);
    await prefs.setInt('port', int.parse(_portController.text));

    // Update the current IP and port state variables
    setState(() {
      _currentIP = _ipController.text;
      _currentPort = int.parse(_portController.text);
    });

    // Update the global IP address and port
    GlobalVariables.ipAddress = _ipController.text;
    GlobalVariables.port = int.parse(_portController.text);

    // Close the existing connection
    NetworkClient().closeConnection();

    // Initialize a new connection with the new IP address and port
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
            Padding(
              padding: EdgeInsets.only(top: 20.0), // Adjust the value as needed
              child: Text('Current Port: $_currentPort'), // Display the current port
            ), // Display the current port
            TextField(
              controller: _portController,
              decoration: InputDecoration(
                labelText: 'New Port',
              ),
              keyboardType: TextInputType.number,
            ),
            ElevatedButton(
              child: Text('Save'),
              onPressed: _saveSettings,
            ),
            ValueListenableBuilder<bool>(
              valueListenable: NetworkClient().connectionStatus,
              builder: (BuildContext context, bool isConnected, Widget? child) {
                return Padding(
                  padding: const EdgeInsets.only(top: 20.0), // Adjust the value as needed
                  child: RichText(
                    text: TextSpan(
                      text: 'Connected to server: ',
                      style: DefaultTextStyle.of(context).style,
                      children: <TextSpan>[
                        TextSpan(
                          text: isConnected ? 'Yes' : 'No',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                );
              },
            )
          ],
        ),
      ),
    );
  }
}