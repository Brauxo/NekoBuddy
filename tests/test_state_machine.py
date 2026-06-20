import time
from src.core.state_machine import StateMachine, PetState

def test_initial_state():
    """Verifies that the state machine initializes with correct default state and mood."""
    sm = StateMachine()
    assert sm.current_state == PetState.IDLE
    assert sm.current_mood == "OBSERVANT"

def test_change_state():
    """Verifies that transitioning states updates the active state and sets random walk directions."""
    sm = StateMachine()
    sm.change_state(PetState.WALKING)
    assert sm.current_state == PetState.WALKING
    assert sm.walk_dir in [
        (0, -1), (0, 1), (-1, 0), (1, 0),
        (-1, -1), (1, -1), (-1, 1), (1, 1)
    ]

def test_set_mood():
    """Verifies that moods are sanitized and update the behavioral mood variables."""
    sm = StateMachine()
    sm.set_mood("lazy")
    assert sm.current_mood == "LAZY"
    
    # Verify invalid moods are rejected and keep the previous mood
    sm.set_mood("excited")
    assert sm.current_mood == "LAZY"
