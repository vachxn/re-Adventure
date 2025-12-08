"""
Sprite and animation management
"""
import os
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QRect


class SpriteSheet:
    """Manages a sprite sheet with animations"""
    
    def __init__(self, image_path, frame_width=32, frame_height=32, animations=None):
        """
        Load a sprite sheet
        
        Args:
            image_path: Path to sprite sheet image
            frame_width: Width of each frame
            frame_height: Height of each frame
            animations: Dict mapping animation names to row indices
        """
        self.pixmap = QPixmap(image_path)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames_per_row = 4  # Standard: 4 frames per animation
        
        if animations is None:
            self.animations = {
                "idle": 0,
                "walk_down": 1,
                "walk_up": 2,
                "walk_left": 3,
                "walk_right": 4,
                "attack_down": 5,
                "attack_up": 6,
                "attack_left": 7,
                "attack_right": 8,
                "died": 9
            }
        else:
            self.animations = animations
            
    def get_frame(self, animation, frame_index):
        """Get a specific frame from an animation"""
        # Check if animation exists, otherwise use fallback
        if animation not in self.animations:
            # Try to find a similar animation or use idle
            if animation.startswith("walk_"):
                # Fallback: try generic walk
                if "walk_down" in self.animations:
                    animation = "walk_down"
                elif "walk" in self.animations:
                    animation = "walk"
                else:
                    animation = "idle"
            elif animation.startswith("attack_"):
                # Fallback: try generic attack
                if "attack_down" in self.animations:
                    animation = "attack_down"
                elif "attack" in self.animations:
                    animation = "attack"
                else:
                    animation = "idle"
            else:
                animation = "idle"
            
        row = self.animations[animation]
        frame_index = frame_index % self.frames_per_row
        
        x = frame_index * self.frame_width
        y = row * self.frame_height
        
        return self.pixmap.copy(x, y, self.frame_width, self.frame_height)


class AnimatedSprite:
    """Animated sprite with state tracking"""
    
    def __init__(self, sprite_sheet):
        self.sprite_sheet = sprite_sheet
        self.current_animation = "idle"
        self.current_frame = 0
        self.frame_time = 0
        self.frame_duration = 0.15  # Seconds per frame
        
    def set_animation(self, animation):
        """Set current animation"""
        if animation != self.current_animation:
            self.current_animation = animation
            self.current_frame = 0
            self.frame_time = 0
            
    def update(self, dt):
        """Update animation"""
        self.frame_time += dt
        
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            self.current_frame = (self.current_frame + 1) % self.sprite_sheet.frames_per_row
            
    def get_current_frame(self):
        """Get current frame pixmap"""
        return self.sprite_sheet.get_frame(self.current_animation, self.current_frame)


class SpriteManager:
    """Manages all game sprites"""
    
    def __init__(self):
        self.sprites = {}
        self.load_sprites()
        
    def load_sprites(self):
        """Load all sprite sheets"""
        # Get base path
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
        
        # Check if sprites exist
        if not os.path.exists(base_path):
            print(f"Sprites folder not found at {base_path}")
            print("Run generator.py to create sprites")
            return
            
        # Load animated sprites (32x32 frames in 128x128 sheet)
        sprite_files = {
            "player": "player.png",
            "dragon_red": "dragon_red.png",
            "dragon_yellow": "dragon_yellow.png",
            "dragon_green": "dragon_green.png",
            "bat": "bat.png"
        }
        
        for name, filename in sprite_files.items():
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                self.sprites[name] = SpriteSheet(path, 32, 32)
            else:
                print(f"Warning: {filename} not found")
                
        # Load static item sprites (32x32)
        item_files = {
            "sword": "sword.png",
            "key_gold": "key_gold.png",
            "key_silver": "key_silver.png",
            "chalice": "chalice.png"
        }
        
        for name, filename in item_files.items():
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                # Items are static, but we still wrap them
                pixmap = QPixmap(path)
                self.sprites[name] = pixmap
            else:
                print(f"Warning: {filename} not found")
                
    def get_sprite_sheet(self, name):
        """Get a sprite sheet by name"""
        return self.sprites.get(name)
        
    def create_animated_sprite(self, entity_type):
        """Create an animated sprite for an entity"""
        sprite_sheet = self.get_sprite_sheet(entity_type)
        if sprite_sheet and isinstance(sprite_sheet, SpriteSheet):
            return AnimatedSprite(sprite_sheet)
        return None
        
    def get_hit_sprite(self, sprite_type):
        """Get the hit sprite for a given sprite type"""
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
        hit_file = os.path.join(base_path, f"{sprite_type}-hit.png")
        
        if os.path.exists(hit_file):
            pixmap = QPixmap(hit_file)
            if not pixmap.isNull():
                return pixmap
        return None
        
    def get_hit_sprite(self, sprite_type):
        """Get the hit sprite for a given sprite type"""
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
        hit_file = os.path.join(base_path, f"{sprite_type}-hit.png")
        
        if os.path.exists(hit_file):
            pixmap = QPixmap(hit_file)
            if not pixmap.isNull():
                return pixmap
        return None

