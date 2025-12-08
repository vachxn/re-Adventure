"""
Game state management
"""
import json
import os
from typing import Set, Optional
from PyQt6.QtCore import Qt
from engine.world import World, Room
from engine.entities import Player
from engine.systems import MovementSystem, CollisionSystem, CombatSystem
from engine.audio_manager import AudioManager
from engine.language_manager import LanguageManager


class GameState:
    """Main game state"""
    
    def __init__(self):
        # World
        self.world = World()
        self.current_room: Optional[Room] = None
        
        # Player
        self.player: Optional[Player] = None
        
        # Game state
        self.game_over = False
        self.game_won = False
        self.last_message = ""
        
        # Track unlocked doors: set of (room_id, direction) tuples
        self.unlocked_doors = set()
        
        # Timing
        self.damage_cooldown = 0  # Prevent damage spam
        self.attack_cooldown = 0  # Prevent attack spam
        self.transition_cooldown = 0  # Prevent rapid room transitions
        
        # Audio
        self.audio_manager = AudioManager()
        
        # Language manager
        self.language_manager = LanguageManager("english")
        
        # Initialize game
        self.initialize_game()
        
    def initialize_game(self):
        """Initialize a new game"""
        # Load world data
        self.load_world()
        
        # Create player
        if self.world.starting_room_id:
            starting_room = self.world.get_room(self.world.starting_room_id)
            if starting_room:
                spawn_x, spawn_y = starting_room.player_spawn
                self.player = Player(spawn_x, spawn_y)
                self.current_room = starting_room
                
    def load_world(self):
        """Load world from JSON file"""
        try:
            # Get the path to the data folder relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(current_dir, "..", "data", "rooms.json")
            
            with open(data_path, "r") as f:
                data = json.load(f)
                self.world.load_from_json(data)
        except FileNotFoundError as e:
            print(f"Could not find rooms.json at {data_path}")
            # Create a default world if file doesn't exist
            self.create_default_world()
            
    def create_default_world(self):
        """Create a simple default world for testing"""
        from engine.entities import Enemy, Item
        
        # Create starting room
        room1 = Room("start", "Castle Entrance", "castle")
        room1.set_exit("east", "treasure")
        room1.set_exit("north", "danger")
        room1.player_spawn = (100, 240)
        room1.add_entity(Item(200, 240, "sword"))
        self.world.add_room(room1)
        
        # Create treasure room
        room2 = Room("treasure", "Treasure Room", "castle")
        room2.set_exit("west", "start")
        room2.player_spawn = (100, 240)
        room2.add_entity(Item(400, 240, "key_gold"))
        room2.add_entity(Item(500, 240, "chalice"))
        self.world.add_room(room2)
        
        # Create danger room
        room3 = Room("danger", "Dragon's Lair", "dungeon")
        room3.set_exit("south", "start")
        room3.player_spawn = (320, 400)
        room3.add_entity(Enemy(320, 150, "dragon_red"))
        room3.add_entity(Item(320, 50, "key_silver"))
        self.world.add_room(room3)
        
        self.world.set_starting_room("start")
        
    def update(self, pressed_keys: Set[int]):
        """Update game state"""
        if self.game_over:
            return
            
        if not self.player or not self.current_room:
            return
            
        # Update cooldowns
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 0.016
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 0.016
        if self.transition_cooldown > 0:
            self.transition_cooldown -= 0.016
            
        # Update damage flash effect
        if self.player.damage_flash_count > 0:
            self.player.damage_flash_timer -= 0.016
            if self.player.damage_flash_timer <= 0:
                # Flash completed, move to pause or next flash
                if self.player.damage_flash_timer <= -0.1:  # Pause completed, start next flash
                    self.player.damage_flash_count -= 1
                    if self.player.damage_flash_count > 0:
                        # Start next flash
                        self.player.damage_flash_timer = 0.1  # Flash duration
                    else:
                        # All flashes done
                        self.player.damage_flash_timer = 0
                        self.player.damage_flash_count = 0
                else:  # Flash just ended, start pause
                    # Pause between flashes (0.1 second)
                    self.player.damage_flash_timer = -0.1  # Negative indicates pause
            
        # Update player movement
        exit_direction = MovementSystem.update_player_movement(
            self.player, pressed_keys, self.current_room
        )
        
        # Handle footstep sounds
        if self.player.animation_state.startswith("walk_"):
            # Start footsteps if not already playing
            if not self.audio_manager.is_sound_playing("footsteps"):
                self.audio_manager.play_sound("footsteps")
        else:
            # Stop footsteps when not walking
            if self.audio_manager.is_sound_playing("footsteps"):
                self.audio_manager.stop_sound("footsteps")
        
        # Handle room transitions (with cooldown to prevent rapid switching)
        if exit_direction and self.transition_cooldown <= 0:
            self.transition_room(exit_direction)
            self.transition_cooldown = 0.5  # Half second cooldown between transitions
            
        # Update enemy AI and cooldowns
        for entity in self.current_room.entities:
            from engine.entities import Enemy
            if isinstance(entity, Enemy) and entity.alive:
                # Update attack cooldown
                if entity.attack_cooldown > 0:
                    entity.attack_cooldown -= 0.016  # ~60 FPS
                    
                MovementSystem.update_enemy_ai(entity, self.player, self.current_room)
                
        # Check item pickups
        pickup_message = CollisionSystem.check_item_pickups(self.player, self.current_room)
        if pickup_message:
            self.last_message = pickup_message
            # Play item collection sound
            self.audio_manager.play_sound("item_collected")
            
        # Handle combat
        if self.attack_cooldown <= 0:
            attack_message = CombatSystem.player_attack(self.player, self.current_room, pressed_keys, self.audio_manager, self.language_manager)
            if attack_message:
                self.last_message = attack_message
                self.attack_cooldown = 0.5  # Half second cooldown
                
        # Check collisions and damage
        if self.damage_cooldown <= 0:
            if CollisionSystem.check_enemy_collisions(self.player, self.current_room):
                self.player.take_damage(1)
                # Trigger damage flash (2 flashes)
                self.player.damage_flash_count = 2
                self.player.damage_flash_timer = 0.1  # Flash duration
                self.last_message = self.language_manager.get("messages.took_damage", "Ouch! Took damage!")
                self.damage_cooldown = 1.0  # 1 second invulnerability
                # Play hurt sound
                self.audio_manager.play_sound("player_hurt")
                
                if not self.player.alive:
                    self.game_over = True
                    self.last_message = self.language_manager.get("messages.game_over", "Game Over! You died.")
                    
            elif CollisionSystem.check_hazard_collisions(self.player, self.current_room):
                self.player.take_damage(1)
                # Trigger damage flash (2 flashes)
                self.player.damage_flash_count = 2
                self.player.damage_flash_timer = 0.1  # Flash duration
                self.last_message = self.language_manager.get("messages.hit_hazard", "Hit a hazard!")
                self.damage_cooldown = 1.0
                # Play hurt sound
                self.audio_manager.play_sound("player_hurt")
                
                if not self.player.alive:
                    self.game_over = True
                    self.last_message = self.language_manager.get("messages.game_over", "Game Over! You died.")
                    
        # Cleanup dead entities
        self.current_room.cleanup_dead_entities()
        
        # Check win condition (has chalice)
        if "chalice" in self.player.quest_items and not self.game_won:
            self.game_won = True
            self.last_message = self.language_manager.get("messages.victory", "Victory! You found the Enchanted Chalice!")
            
    def transition_room(self, direction: str):
        """Transition to a new room"""
        next_room_id = self.current_room.get_exit(direction)
        if not next_room_id:
            return
        
        # Check if door is locked
        door_key = (self.current_room.room_id, direction)
        is_locked = self.current_room.is_exit_locked(direction)
        is_unlocked = door_key in self.unlocked_doors
        
        if is_locked and not is_unlocked:
            # Check if player has the required key
            required_key = self.current_room.get_exit_key(direction)
            if required_key and self.player.has_key(required_key):
                # Unlock the door and consume the key
                self.unlocked_doors.add(door_key)
                self.player.keys.remove(required_key)
                unlock_text = self.language_manager.get("messages.door_unlocked", "Unlocked the door with the {key} key!")
                key_display = required_key.capitalize()
                self.last_message = unlock_text.replace("{key}", key_display)
                # Continue to transition
            else:
                # Door is locked and player doesn't have the key
                required_key = self.current_room.get_exit_key(direction)
                if required_key:
                    key_display = required_key.capitalize()
                    locked_text = self.language_manager.get("messages.door_locked", "The door is locked! Requires {key} Key.")
                    self.last_message = locked_text.replace("{key}", key_display)
                else:
                    locked_text = self.language_manager.get("messages.door_locked", "The door is locked!")
                    self.last_message = locked_text
                return
            
        next_room = self.world.get_room(next_room_id)
        if not next_room:
            return
            
        # Move player to opposite side of new room (well inside the bounds)
        if direction == "north":
            self.player.set_position(self.player.x, 440)  # Bottom of new room
        elif direction == "south":
            self.player.set_position(self.player.x, 30)  # Top of new room
        elif direction == "east":
            self.player.set_position(30, self.player.y)  # Left of new room
        elif direction == "west":
            self.player.set_position(590, self.player.y)  # Right of new room
            
        self.current_room = next_room
        entered_text = self.language_manager.get("messages.entered_room", "Entered {room}")
        self.last_message = entered_text.replace("{room}", next_room.name)
        
    def save_game(self, filename: str):
        """Save game state to file"""
        save_data = {
            "current_room": self.current_room.room_id if self.current_room else None,
            "player": {
                "x": self.player.x,
                "y": self.player.y,
                "health": self.player.health,
                "has_sword": self.player.has_sword,
                "keys": self.player.keys,
                "quest_items": self.player.quest_items
            },
            "unlocked_doors": list(self.unlocked_doors),  # Save unlocked doors
            "dead_enemies": [],  # Track which enemies are dead
            "collected_items": []  # Track which items are collected
        }
        
        with open(f"data/saves/{filename}", "w") as f:
            json.dump(save_data, f, indent=2)
            
    def load_game(self, filename: str):
        """Load game state from file"""
        try:
            with open(f"data/saves/{filename}", "r") as f:
                save_data = json.load(f)
                
            # Restore player
            player_data = save_data["player"]
            self.player = Player(player_data["x"], player_data["y"])
            self.player.health = player_data["health"]
            self.player.has_sword = player_data["has_sword"]
            self.player.keys = player_data["keys"]
            self.player.quest_items = player_data["quest_items"]
            
            # Restore room
            room_id = save_data["current_room"]
            self.current_room = self.world.get_room(room_id)
            
            # Restore unlocked doors
            if "unlocked_doors" in save_data:
                self.unlocked_doors = set(tuple(door) for door in save_data["unlocked_doors"])
            
            self.last_message = self.language_manager.get("messages.game_loaded", "Game loaded!")
            
        except FileNotFoundError:
            self.last_message = "Save file not found!"

