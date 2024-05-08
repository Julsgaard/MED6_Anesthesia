import 'dart:ui';
import 'dart:developer' as developer; // Import for logging
import 'package:flutter/cupertino.dart';

enum States {
  blinking,
  intro,
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

  States _currentState = States.mouthOpeningIntro; // Initial state set to MouthOpening
// Initial state set to MouthOpening
  States _previousState = States.mouthOpeningIntro; // Use this to keep track of which state the user was in in case of the state being aborted

  List<VoidCallback> _listeners = []; // Listeners to notify upon state change

  States get currentState => _currentState; // Getter for the current state
  States get previousState => _previousState; // Getter for the previous state

  void addListener(VoidCallback listener) {
    _listeners.add(listener); // Method to add a listener
    print(_listeners);
  }

  void notifyListeners() {
    //print("I NOTIFY LISTENERS");
    for (var listener in _listeners) { // Notify all listeners of a state change
        listener();
    }
  }

  void changeState(States newState) {
    if (_currentState == newState) return; // If the requested state is the same as the current state, do nothing
    developer.log("Changing current state to $newState while old state was $_previousState");
    // If the current state is not error state, change the state to the requested state and save the previous state
    if (_currentState.index < 9) {
      developer.log("UNDER 9??");
      _previousState = _currentState;
      _currentState = newState;
    }

    // If the current state is error state, ignore whatever state change is requested and change to previous state (IDK BUT THIS WORKS)
    else if (_currentState.index >= 9) {
      developer.log("OVER 9??");
      _currentState = _previousState;
    }
    notifyListeners(); // Notify all listeners about the state change
  }

  void removeListener(VoidCallback listener) {
    _listeners.remove(listener); // Method to remove a listener
  }
}
