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
  bool _showState = GlobalVariables.showState; // Use a local copy for the widget

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  _loadSettings() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? ipAddress = prefs.getString('ipAddress');
    int? port = prefs.getInt('port');
    bool? showState = prefs.getBool('showState') ?? GlobalVariables.showState; // Retrieve or use default
    if (ipAddress != null) {
      setState(() {
        _currentIP = ipAddress;
        _ipController.text = ipAddress;
        _showState = showState;
      });
    }
    else {
      setState(() {
        _currentIP = GlobalVariables.ipAddress;
        _showState = showState;
      });
    }
    if (port != null) {
      setState(() {
        _currentPort = port;
        _portController.text = port.toString();
        _showState = showState;
      });
    }
    else {
      setState(() {
        _currentPort = GlobalVariables.port; // Default port
        _portController.text = GlobalVariables.port.toString(); // Default port as a string
        _showState = showState;
      });
    }
  }

  _saveSettings() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('ipAddress', _ipController.text);
    await prefs.setInt('port', int.parse(_portController.text));
    await prefs.setBool('showState', _showState); // Save the state of showState

    // Update the current IP and port state variables
    setState(() {
      _currentIP = _ipController.text;
      _currentPort = int.parse(_portController.text);
    });

    // Update the global IP address and port
    GlobalVariables.ipAddress = _ipController.text;
    GlobalVariables.port = int.parse(_portController.text);
    GlobalVariables.showState = _showState;

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
            SwitchListTile(
              title: Text('Show Current State'),
              value: _showState,
              onChanged: (bool value) {
                setState(() {
                  _showState = value;
                });
              },
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