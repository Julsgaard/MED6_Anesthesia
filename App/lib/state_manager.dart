import 'dart:ui';

enum States {
  mouthOpening,
  mallampati,
  neckMovement,
  errorState
  // ThyromentalDistance,
  // AbilityToPrognath
}

class StateManager {
  States _currentState = States.mouthOpening; // Initial state set to MouthOpening
  States _previousState = States.mouthOpening; // Use this to keep track of which state the user was in in case of the state being aborted
  List<VoidCallback> _listeners = []; // Listeners to notify upon state change

  States get currentState => _currentState; // Getter for the current state
  States get previousState => _previousState; // Getter for the previous state

  void addListener(VoidCallback listener) {
    _listeners.add(listener); // Method to add a listener
  }

  void notifyListeners() {
    for (var listener in _listeners) {
      listener(); // Notify all listeners of a state change
    }
  }

  void changeState(States newState) {
    print("Changing current state to $newState while old state was $_previousState");
    // If the current state is not error state, change the state to the requested state and save the previous state
    if (_currentState != States.errorState) {
      _previousState = _currentState;
      _currentState = newState;
    }

    // If the current state is error state, ignore whatever state change is requested and change to previous state (IDK BUT THIS WORKS)
    else if (_currentState == States.errorState) {
      _currentState = _previousState;
    }
    notifyListeners(); // Notify all listeners about the state change
  }

  void removeListener(void Function() onStateChanged) {
    _listeners.remove(onStateChanged); // Method to remove a listener
  }
}
