import 'dart:ui';
import 'dart:developer' as developer; // Import for logging
import 'package:flutter/cupertino.dart';

enum States {
  intro,
  inputPage,
  mouthOpeningIntro,
  mouthOpeningExercise,
  mallampatiIntro,
  mallampatiExercise,
  neckMovementIntro,
  neckMovementExercise,
  thanks,
  oopsEyeHeight,
  oopsFaceParallel,
  oopsNoFace,
  oopsBrightness
  // ThyromentalDistance,
  // AbilityToPrognath
}


class StateManager {
  final int _errorStateIndex = 9;
  States _currentState = States.intro; // Initial state set to MouthOpening
// Initial state set to MouthOpening
  States _previousState = States.intro; // Use this to keep track of which state the user was in in case of the state being aborted
  List<dynamic> _listeners = []; // Listeners to notify upon state change

  States get currentState => _currentState; // Getter for the current state
  States get previousState => _previousState; // Getter for the previous state
  int get errorStateIndex => _errorStateIndex; // Getter for the error state index

  void addListener(dynamic listener) {
    _listeners.add(listener); // Method to add a listener
    print(_listeners);
  }

  Future<void> notifyListeners() async{
    print("I NOTIFY LISTENERS");
    if (_listeners.isEmpty) return; // If there are no listeners, do nothing
    for (var listener in _listeners) {
      if (listener is Function()) {
        listener(); // Notify all listeners
      }else if(listener is Future Function()){
        await listener();
      }
    }
  }

  void changeState(States newState) {
    if (_currentState == newState) return; // If the requested state is the same as the current state, do nothing
    //developer.log("Changing current state to $newState while old state was $_previousState");
    // If the current state is not error state, change the state to the requested state and save the previous state
    if (_currentState.index < _errorStateIndex) {
      //developer.log("UNDER 8");
      _previousState = _currentState;
      _currentState = newState;
    }

    // If the current state is error state, ignore whatever state change is requested and change to previous state (IDK BUT THIS WORKS)
    else if (_currentState.index >= _errorStateIndex) {
      //developer.log("OVER 8??");
      _currentState = _previousState;
    }
    notifyListeners(); // Notify all listeners about the state change
  }

  void removeListener(dynamic listener) {
    _listeners.remove(listener); // Method to remove a listener
  }

  void nextState(){
    int nextIndex = _currentState.index+1;
    if(nextIndex < _errorStateIndex){
      _previousState = _currentState;
      _currentState = States.values[nextIndex];
      notifyListeners();
    }

  }
}
