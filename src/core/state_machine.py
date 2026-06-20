from enum import Enum, auto
import random
import time

class PetState(Enum):
    IDLE = auto()
    WALKING = auto()
    THINKING = auto()
    SPEAKING = auto()
    SLEEPING = auto()
    WASHING = auto()
    YAWNING = auto()
    SCRATCHING = auto()

class StateMachine:
    """
    Manages the current state of the desktop companion.
    Includes logic for random state transitions based on the current MOOD.
    """
    def __init__(self):
        self.current_state = PetState.IDLE
        self.state_start_time = time.time()
        self.walk_dir = (1, 0)
        self.current_mood = "OBSERVANT"
        
    def set_mood(self, mood: str):
        """Updates the mood, shifting autonomous behavior probabilities."""
        valid_moods = ["ENERGETIC", "LAZY", "GROOMING", "OBSERVANT"]
        mood_upper = mood.upper()
        if mood_upper in valid_moods:
            self.current_mood = mood_upper
        
    def change_state(self, new_state: PetState):
        """Transition to a new state and record the time."""
        if self.current_state != new_state:
            self.current_state = new_state
            self.state_start_time = time.time()
            
            # If we decide to walk, pick a random 2D direction
            if new_state == PetState.WALKING:
                directions = [
                    (0, -1), (0, 1), (-1, 0), (1, 0),   # Up, Down, Left, Right
                    (-1, -1), (1, -1), (-1, 1), (1, 1)  # Diagonals
                ]
                self.walk_dir = random.choice(directions)

    def get_time_in_state(self) -> float:
        """Returns the number of seconds the pet has been in the current state."""
        return time.time() - self.state_start_time

    def update(self):
        """Called every frame to handle state transitions based on time elapsed and mood probabilities."""
        if self.current_state in (PetState.THINKING, PetState.SPEAKING):
            return

        time_in_state = self.get_time_in_state()

        if self.current_state == PetState.IDLE:
            # Randomly do an action after a short while so it's more active
            if time_in_state > random.uniform(2.0, 5.0):
                # Shift weights based on the current mood
                # Weights map to: [WALKING, SLEEPING, WASHING, YAWNING, SCRATCHING]
                if self.current_mood == "LAZY":
                    weights = [0.1, 0.7, 0.05, 0.1, 0.05]
                elif self.current_mood == "ENERGETIC":
                    weights = [0.8, 0.0, 0.05, 0.05, 0.1]
                elif self.current_mood == "GROOMING":
                    weights = [0.2, 0.05, 0.6, 0.05, 0.1]
                else: # OBSERVANT
                    weights = [0.3, 0.05, 0.05, 0.1, 0.5]
                
                action = random.choices(
                    [PetState.WALKING, PetState.SLEEPING, PetState.WASHING, PetState.YAWNING, PetState.SCRATCHING],
                    weights=weights
                )[0]
                self.change_state(action)

        elif self.current_state == PetState.WALKING:
            # Walk for a longer duration
            if time_in_state > random.uniform(4.0, 10.0):
                self.change_state(PetState.IDLE)
                
        elif self.current_state in (PetState.WASHING, PetState.YAWNING, PetState.SCRATCHING):
            # These are quick animations, go back to idle after a few seconds
            if time_in_state > random.uniform(3.0, 5.0):
                self.change_state(PetState.IDLE)
                
        elif self.current_state == PetState.SLEEPING:
            # Wake up eventually
            if time_in_state > random.uniform(10.0, 30.0):
                self.change_state(PetState.IDLE)
