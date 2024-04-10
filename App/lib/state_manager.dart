import 'dart:ui';

enum States {
  mouthOpening,
  mallampati,
  neckMovement
  // ThyromentalDistance,
  // AbilityToPrognath
}

class StateManager {
  States _currentState = States.mouthOpening; // Initial state set to MouthOpening
  List<VoidCallback> _listeners = []; // Listeners to notify upon state change

  States get currentState => _currentState; // Getter for the current state

  void addListener(VoidCallback listener) {
    _listeners.add(listener); // Method to add a listener
  }

  void notifyListeners() {
    for (var listener in _listeners) {
      listener(); // Notify all listeners of a state change
    }
  }

  void changeState(States newState) {
    _currentState = newState; // Change the current state
    notifyListeners(); // Notify all listeners about the state change
  }

  void removeListener(void Function() onStateChanged) {
    _listeners.remove(onStateChanged); // Method to remove a listener
  }
}
