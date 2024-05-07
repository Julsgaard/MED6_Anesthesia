import 'dart:ui';

import 'package:flutter/cupertino.dart';

enum States {
  blinking,
  mouthOpeningExercise,
  mouthOpeningIntro,
  mallampatiExercise,
  mallampatiIntro,
  neckMovementExercise,
  neckMovementIntro,
  intro,
  thanks,
  oopsEyeHeight,
  oopsFaceParallel,

  // ThyromentalDistance,
  // AbilityToPrognath
}


class StateManager {
  States _currentState = States.mouthOpeningIntro; // Initial state set to MouthOpening
  List<VoidCallback> _listeners = []; // Listeners to notify upon state change

  States get currentState => _currentState; // Getter for the current state

  void addListener(VoidCallback listener) {
    _listeners.add(listener); // Method to add a listener
    print(_listeners);
  }

  void notifyListeners() {
    print("I NOTIFY LISTENERS");
    for (var listener in _listeners) { // Notify all listeners of a state change
        listener();
    }
  }

  void changeState(States newState) {
    _currentState = newState; // Change the current state
    notifyListeners(); // Notify all listeners about the state change
  }

  void removeListener(VoidCallback listener) {
    _listeners.remove(listener); // Method to remove a listener
  }
}
