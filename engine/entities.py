"""
Entity classes: Player, Enemy, Item, Hazard
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Hitbox:
    """Simple AABB hitbox"""
    x: float
    y: float
    width: float
    height: float
    
    def intersects(self, other: 'Hitbox') -> bool:
        """Check if this hitbox intersects another"""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
    
    def get_combat_hitbox(self, buffer: float = 3.0) -> 'Hitbox':
        """Get a larger combat hitbox with buffer around this hitbox"""
        return Hitbox(
            self.x - buffer,
            self.y - buffer,
            self.width + (buffer * 2),
            self.height + (buffer * 2)
        )
    
    def copy(self):
        """Create a copy of this hitbox"""
        return Hitbox(self.x, self.y, self.width, self.height)


class Entity:
    """Base entity class"""
    
    _id_counter = 0
    
    def __init__(self, x: float, y: float, width: float = 16, height: float = 16):
        self.entity_id = Entity._id_counter
        Entity._id_counter += 1
        
        self.x = x
        self.y = y
        self.hitbox = Hitbox(x, y, width, height)
        self.sprite = None
        self.flags = {}
        self.alive = True
        
        # Animation state
        self.animation_state = "idle"
        self.last_dx = 0
        self.last_dy = 0
        self.facing_direction = "down"  # down, up, left, right
        
    def update_hitbox(self):
        """Update hitbox position"""
        self.hitbox.x = self.x
        self.hitbox.y = self.y
        
    def move(self, dx: float, dy: float):
        """Move entity by delta"""
        self.x += dx
        self.y += dy
        self.update_hitbox()
        
    def set_position(self, x: float, y: float):
        """Set entity position"""
        self.x = x
        self.y = y
        self.update_hitbox()


class Player(Entity):
    """Player entity"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24, 24)
        self.max_health = 3
        self.health = 3
        self.speed = 3.0
        
        # Inventory
        self.has_sword = False
        self.keys = []  # List of key types (e.g., "gold", "silver")
        self.quest_items = []  # List of quest item names
        
        # Combat state
        self.is_attacking = False
        self.attack_timer = 0
        
        # Damage flash effect
        self.damage_flash_timer = 0  # Timer for damage flash effect
        self.damage_flash_count = 0  # Number of flashes remaining
        
    def take_damage(self, amount: int = 1):
        """Take damage"""
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.alive = False
            
    def heal(self, amount: int = 1):
        """Heal player"""
        self.health = min(self.max_health, self.health + amount)
        
    def add_key(self, key_type: str):
        """Add a key to inventory"""
        if key_type not in self.keys:
            self.keys.append(key_type)
            
    def has_key(self, key_type: str) -> bool:
        """Check if player has a specific key"""
        return key_type in self.keys
        
    def add_quest_item(self, item_name: str):
        """Add a quest item"""
        if item_name not in self.quest_items:
            self.quest_items.append(item_name)


class Enemy(Entity):
    """Enemy entity"""
    
    def __init__(self, x: float, y: float, subtype: str = "dragon_red"):
        super().__init__(x, y, 28, 28)
        self.subtype = subtype
        self.health = 3
        self.damage = 1
        self.speed = 1.5
        self.ai_state = "idle"  # idle, chase, flee, patrol
        self.ai_timer = 0
        self.patrol_direction = 0
        self.attack_cooldown = 0  # Cooldown between attacks (seconds)
        
    def take_damage(self, amount: int = 1):
        """Take damage"""
        self.health -= amount
        if self.health <= 0:
            self.alive = False


class Item(Entity):
    """Collectible item"""
    
    def __init__(self, x: float, y: float, subtype: str = "key_gold"):
        super().__init__(x, y, 16, 16)
        self.subtype = subtype
        self.collected = False
        
    def collect(self, player: Player, language_manager=None):
        """Collect this item"""
        if self.collected:
            return None
            
        self.collected = True
        self.alive = False
        
        # Use language manager if available
        if language_manager:
            # Handle different item types
            if self.subtype.startswith("key_"):
                key_type = self.subtype.replace("key_", "")
                player.add_key(key_type)
                # Capitalize first letter
                display_name = key_type.capitalize()
                found_key = language_manager.get("messages.found_key", "Found {key_type} Key!")
                return found_key.replace("{key_type}", display_name)
                
            elif self.subtype == "sword":
                player.has_sword = True
                return language_manager.get("messages.found_sword", "Found the Sword!")
                
            elif self.subtype == "chalice":
                player.add_quest_item("chalice")
                return language_manager.get("messages.found_chalice", "Found the Enchanted Chalice!")
                
            else:
                player.add_quest_item(self.subtype)
                found_item = language_manager.get("messages.found_item", "Found {item}!")
                return found_item.replace("{item}", self.subtype)
        else:
            # Fallback to English
            if self.subtype.startswith("key_"):
                key_type = self.subtype.replace("key_", "")
                player.add_key(key_type)
                display_name = key_type.capitalize()
                return f"Found {display_name} Key!"
            elif self.subtype == "sword":
                player.has_sword = True
                return "Found the Sword!"
            elif self.subtype == "chalice":
                player.add_quest_item("chalice")
                return "Found the Enchanted Chalice!"
            else:
                player.add_quest_item(self.subtype)
                return f"Found {self.subtype}!"


class Hazard(Entity):
    """Environmental hazard"""
    
    def __init__(self, x: float, y: float, hazard_type: str = "spike"):
        super().__init__(x, y, 16, 16)
        self.hazard_type = hazard_type
        self.damage = 1
        self.active = True

