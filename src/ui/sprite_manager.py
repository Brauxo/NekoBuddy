from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QRect

class SpriteManager:
    """
    Loads sprite sheets and slices them into individual QPixmap frames.
    Handles scaling for pixel art to remain crisp.
    Assumes 32x32 frames organized by rows for different animations.
    """
    def __init__(self, sprite_path: str, frame_width: int = 32, frame_height: int = 32, scale_factor: int = 4) -> None:
        self.sprite_path = sprite_path
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale_factor = scale_factor
        
        self.sheet = QPixmap(self.sprite_path)
        if self.sheet.isNull():
            print(f"Failed to load sprite sheet: {self.sprite_path}")

    def get_animation_sequence(self, config) -> list[QPixmap]:
        """
        Extracts a sequence of frames based on AnimConfig.
        For example, config.row=36 means y = 36 * 32 = 1152.
        """
        frames = []
        if self.sheet.isNull():
            return frames
            
        y = config.row * self.frame_height
        
        for i in range(config.frames):
            x = i * self.frame_width
            rect = QRect(x, y, self.frame_width, self.frame_height)
            frame = self.sheet.copy(rect)
            
            scaled_frame = frame.scaled(
                self.frame_width * self.scale_factor,
                self.frame_height * self.scale_factor,
                Qt.IgnoreAspectRatio,
                Qt.FastTransformation
            )
            frames.append(scaled_frame)
            
        return frames
