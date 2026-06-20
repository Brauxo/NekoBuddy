from dataclasses import dataclass

@dataclass
class AnimConfig:
    row: int
    frames: int
    speed_multiplier: float = 1.0  # >1.0 means slower, <1.0 means faster

# Base animation speed in ms
BASE_ANIM_SPEED = 150

# Map specific string names to their animation row in the sprite sheet
# Note: Rows 0, 1, 2, 3 are static directional poses (down, up, left, right), not true animations.
ANIMATIONS = {
    # --- Basic Movement ---
    "walk_down": AnimConfig(row=4, frames=4, speed_multiplier=1.2),  # Fixed by user
    "walk_up": AnimConfig(row=5, frames=4, speed_multiplier=1.2),    # Fixed by user
    "walk_right": AnimConfig(row=6, frames=8, speed_multiplier=0.8),
    "walk_left": AnimConfig(row=7, frames=8, speed_multiplier=0.8),
    
    # --- Diagonal Movement ---
    "walk_diagonal_down_left": AnimConfig(row=8, frames=6, speed_multiplier=0.8),
    "walk_diagonal_down_right": AnimConfig(row=9, frames=6, speed_multiplier=0.8),
    "walk_diagonal_up_right": AnimConfig(row=10, frames=6, speed_multiplier=0.8),
    "walk_diagonal_up_left": AnimConfig(row=11, frames=6, speed_multiplier=0.8),
    
    # --- Running ---
    "run_right": AnimConfig(row=24, frames=8, speed_multiplier=0.5),
    "run_left": AnimConfig(row=25, frames=8, speed_multiplier=0.5),
    
    # --- Eating (Noted for future use) ---
    "eat_down": AnimConfig(row=20, frames=8, speed_multiplier=1.0),
    "eat_up": AnimConfig(row=21, frames=8, speed_multiplier=1.0),
    "eat_left": AnimConfig(row=22, frames=8, speed_multiplier=1.0),
    "eat_right": AnimConfig(row=23, frames=8, speed_multiplier=1.0),
    "eat_diagonal_down_left": AnimConfig(row=24, frames=8, speed_multiplier=1.0),
    "eat_diagonal_down_right": AnimConfig(row=25, frames=8, speed_multiplier=1.0),
    "eat_diagonal_up_right": AnimConfig(row=26, frames=8, speed_multiplier=1.0),
    "eat_diagonal_up_left": AnimConfig(row=27, frames=8, speed_multiplier=1.0),
    
    # --- Talking / Speaking ---
    "sit_talk": AnimConfig(row=28, frames=3, speed_multiplier=1.5),
    "stand_talk": AnimConfig(row=29, frames=3, speed_multiplier=1.5),
    "spread_talk": AnimConfig(row=30, frames=3, speed_multiplier=1.5),
    "spread_talk_2": AnimConfig(row=31, frames=3, speed_multiplier=1.5),
    
    # --- Yawning / Sleepy ---
    "sit_yawn": AnimConfig(row=32, frames=8, speed_multiplier=1.8),
    "stand_yawn": AnimConfig(row=33, frames=8, speed_multiplier=1.8),
    "spread_yawn": AnimConfig(row=34, frames=8, speed_multiplier=1.8),
    "spread_yawn_2": AnimConfig(row=35, frames=8, speed_multiplier=1.8),
    
    # --- Sleeping (Animating Breathing) ---
    "sleep_heart_fast_left": AnimConfig(row=12, frames=2, speed_multiplier=1.5),
    "sleep_heart_fast_right": AnimConfig(row=13, frames=2, speed_multiplier=1.5),
    "sleep_head_down_right": AnimConfig(row=14, frames=2, speed_multiplier=2.0),
    "sleep_head_down_left": AnimConfig(row=15, frames=2, speed_multiplier=2.0),
    "sleep_curl_left": AnimConfig(row=16, frames=2, speed_multiplier=2.5),
    "sleep_curl_right": AnimConfig(row=17, frames=2, speed_multiplier=2.5),
    "sleep_flat_right": AnimConfig(row=18, frames=2, speed_multiplier=2.5),
    "sleep_flat_left": AnimConfig(row=19, frames=2, speed_multiplier=2.5),
    
    # --- Grooming / Idle Actions ---
    "idle_right": AnimConfig(row=36, frames=9, speed_multiplier=1.2),
    "idle_left": AnimConfig(row=37, frames=9, speed_multiplier=1.2),
    "wash_right": AnimConfig(row=38, frames=7, speed_multiplier=1.5),
    "wash_left": AnimConfig(row=39, frames=11, speed_multiplier=1.5),
    "scratch_right": AnimConfig(row=40, frames=11, speed_multiplier=1.2),
    
    # --- Interactivity / Play ---
    "paw_strike_right": AnimConfig(row=48, frames=9, speed_multiplier=0.8),
    "paw_strike_left": AnimConfig(row=49, frames=9, speed_multiplier=0.8),
    "pounce_right": AnimConfig(row=46, frames=7, speed_multiplier=0.6),
    "pounce_left": AnimConfig(row=47, frames=7, speed_multiplier=0.6),
    "jump_right": AnimConfig(row=50, frames=5, speed_multiplier=0.6),
    "jump_left": AnimConfig(row=51, frames=5, speed_multiplier=0.6),
    "land_fall": AnimConfig(row=52, frames=4, speed_multiplier=0.6),
    
    # Keeping aliases for state_machine backward compatibility
    "idle": AnimConfig(row=36, frames=9, speed_multiplier=1.2),
    "sleep": AnimConfig(row=16, frames=2, speed_multiplier=2.5),
    "wash": AnimConfig(row=38, frames=7, speed_multiplier=1.5),
    "yawn": AnimConfig(row=32, frames=8, speed_multiplier=1.8),
    "scratch": AnimConfig(row=40, frames=11, speed_multiplier=1.2),
}
