"""
Game systems: Movement, Collision, Combat, Inventory
"""
from typing import Set, Optional, Tuple
from PyQt6.QtCore import Qt
from engine.entities import Player, Enemy, Item, Hazard, Entity
from engine.world import Room


class MovementSystem:
    """Handles player and AI movement"""
    
    ROOM_BOUNDS = (10, 10, 630, 470)  # Left, Top, Right, Bottom
    
    @staticmethod
    def update_player_movement(player: Player, pressed_keys: Set[int], room: Room) -> Optional[str]:
        """
        Update player movement based on input
        Returns exit direction if player should transition to new room
        """
        dx = 0
        dy = 0
        
        # WASD or Arrow keys
        if Qt.Key.Key_W in pressed_keys or Qt.Key.Key_Up in pressed_keys:
            dy -= player.speed
        if Qt.Key.Key_S in pressed_keys or Qt.Key.Key_Down in pressed_keys:
            dy += player.speed
        if Qt.Key.Key_A in pressed_keys or Qt.Key.Key_Left in pressed_keys:
            dx -= player.speed
        if Qt.Key.Key_D in pressed_keys or Qt.Key.Key_Right in pressed_keys:
            dx += player.speed
            
        # Update animation state when not moving
        if dx == 0 and dy == 0:
            # No movement - set to idle if not attacking
            if not player.is_attacking:
                player.animation_state = "idle"
            return None
            
        # Try to move
        new_x = player.x + dx
        new_y = player.y + dy
        
        # Check room bounds
        left, top, right, bottom = MovementSystem.ROOM_BOUNDS
        
        # Check for room transitions
        if new_x < left and room.exits.get("west"):
            return "west"
        if new_x + player.hitbox.width > right and room.exits.get("east"):
            return "east"
        if new_y < top and room.exits.get("north"):
            return "north"
        if new_y + player.hitbox.height > bottom and room.exits.get("south"):
            return "south"
            
        # Clamp to room bounds
        new_x = max(left, min(right - player.hitbox.width, new_x))
        new_y = max(top, min(bottom - player.hitbox.height, new_y))
        
        # Check collision with entities
        temp_hitbox = player.hitbox.copy()
        temp_hitbox.x = new_x
        temp_hitbox.y = new_y
        
        for entity in room.entities:
            if not entity.alive:
                continue
            if isinstance(entity, Enemy):
                if temp_hitbox.intersects(entity.hitbox):
                    # Can't move through enemies
                    return None
                    
        # Move player
        player.set_position(new_x, new_y)
        
        # Update animation state and facing direction
        if dx != 0 or dy != 0:
            # Determine facing direction based on movement
            if abs(dy) > abs(dx):
                # Moving more vertically
                if dy < 0:
                    player.facing_direction = "up"
                else:
                    player.facing_direction = "down"
            else:
                # Moving more horizontally
                if dx < 0:
                    player.facing_direction = "left"
                else:
                    player.facing_direction = "right"
            
            player.animation_state = f"walk_{player.facing_direction}"
            player.last_dx = dx
            player.last_dy = dy
        else:
            if not player.is_attacking:
                player.animation_state = "idle"
                
        return None
        
    @staticmethod
    def update_enemy_ai(enemy: Enemy, player: Player, room: Room, dt: float = 0.016):
        """Update enemy AI movement"""
        if not enemy.alive:
            enemy.animation_state = "died"
            return
            
        if not player.alive:
            enemy.animation_state = "idle"
            return
            
        enemy.ai_timer += dt
        
        # Simple chase AI
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Determine enemy facing direction toward player
        if abs(dy) > abs(dx):
            if dy < 0:
                enemy.facing_direction = "up"
            else:
                enemy.facing_direction = "down"
        else:
            if dx < 0:
                enemy.facing_direction = "left"
            else:
                enemy.facing_direction = "right"
        
        # Chase if player is detectable (within 200 pixels)
        if distance < 200 and distance > 0:
            enemy.ai_state = "chase"
            enemy.animation_state = f"walk_{enemy.facing_direction}"
            
            # Move towards player
            move_x = (dx / distance) * enemy.speed
            move_y = (dy / distance) * enemy.speed
            
            # Try to move
            new_x = enemy.x + move_x
            new_y = enemy.y + move_y
            
            # Clamp to room bounds
            left, top, right, bottom = MovementSystem.ROOM_BOUNDS
            new_x = max(left, min(right - enemy.hitbox.width, new_x))
            new_y = max(top, min(bottom - enemy.hitbox.height, new_y))
            
            # Check if this position would overlap player's core hitbox
            temp_hitbox = enemy.hitbox.copy()
            temp_hitbox.x = new_x
            temp_hitbox.y = new_y
            
            # Don't allow core hitbox overlap, but allow them to get very close
            if not temp_hitbox.intersects(player.hitbox):
                # Safe to move - no overlap
                enemy.set_position(new_x, new_y)
            # If would overlap, don't move - stay at current position for combat
            
            # Check if in attack range (very close)
            if distance < 35:
                enemy.animation_state = f"attack_{enemy.facing_direction}"
                enemy.ai_state = "attack"
        else:
            # Idle or patrol
            enemy.ai_state = "idle"
            enemy.animation_state = "idle"


class CollisionSystem:
    """Handles collision detection and response"""
    
    # Combat hitbox buffer (3 pixels around entity)
    COMBAT_BUFFER = 3.0
    
    @staticmethod
    def check_item_pickups(player: Player, room: Room, language_manager=None) -> Optional[str]:
        """Check if player is picking up items"""
        for entity in room.entities:
            if isinstance(entity, Item) and entity.alive:
                if player.hitbox.intersects(entity.hitbox):
                    message = entity.collect(player, language_manager)
                    return message
        return None
        
    @staticmethod
    def check_enemy_collisions(player: Player, room: Room) -> bool:
        """Check if player's combat hitbox is touching enemies' combat hitboxes"""
        # Get player's combat hitbox (3px buffer)
        player_combat_box = player.hitbox.get_combat_hitbox(CollisionSystem.COMBAT_BUFFER)
        
        for entity in room.entities:
            if isinstance(entity, Enemy) and entity.alive:
                # Check if enemy can attack (cooldown expired)
                if entity.attack_cooldown > 0:
                    continue  # Enemy is on cooldown, can't attack
                    
                # Get enemy's combat hitbox (3px buffer)
                enemy_combat_box = entity.hitbox.get_combat_hitbox(CollisionSystem.COMBAT_BUFFER)
                
                # Check if combat hitboxes intersect (they are fighting)
                if player_combat_box.intersects(enemy_combat_box):
                    # Enemy attacks - set cooldown
                    entity.attack_cooldown = 1.8  # 1.8 second cooldown
                    return True
        return False
        
    @staticmethod
    def check_hazard_collisions(player: Player, room: Room) -> bool:
        """Check if player is touching hazards"""
        for entity in room.entities:
            if isinstance(entity, Hazard) and entity.active:
                if player.hitbox.intersects(entity.hitbox):
                    return True
        return False


class CombatSystem:
    """Handles combat mechanics"""
    
    # Enemy display names
    ENEMY_NAMES = {
        "dragon_red": "Red Dragon",
        "dragon_yellow": "Yellow Dragon",
        "dragon_green": "Green Dragon",
        "bat": "Bat"
    }
    
    @staticmethod
    def get_enemy_name(subtype: str, language_manager=None) -> str:
        """Get display name for enemy type"""
        if language_manager:
            key = f"enemies.{subtype}"
            return language_manager.get(key, CombatSystem.ENEMY_NAMES.get(subtype, subtype))
        return CombatSystem.ENEMY_NAMES.get(subtype, subtype)
    
    @staticmethod
    def player_attack(player: Player, room: Room, pressed_keys: Set[int], audio_manager=None, language_manager=None) -> Optional[str]:
        """Handle player attack (Space or E key)"""
        if not player.has_sword:
            return None
            
        if Qt.Key.Key_Space not in pressed_keys and Qt.Key.Key_E not in pressed_keys:
            player.is_attacking = False
            # Reset to idle if not moving
            if player.animation_state.startswith("attack_"):
                player.animation_state = "idle"
            return None
            
        # Set attack animation based on facing direction
        player.animation_state = f"attack_{player.facing_direction}"
        player.is_attacking = True
        
        # Get player's combat hitbox for attack range
        player_combat_box = player.hitbox.get_combat_hitbox(40)  # 40 pixel attack range
            
        # Attack: damage enemies within combat range
        for entity in room.entities:
            if isinstance(entity, Enemy) and entity.alive:
                # Check if enemy is in attack range using combat hitboxes
                if player_combat_box.intersects(entity.hitbox):
                    entity.take_damage(1)
                    enemy_name = CombatSystem.get_enemy_name(entity.subtype, language_manager)
                    
                    # Play sword hit sound
                    if audio_manager:
                        audio_manager.play_sound("sword_hit")
                    
                    if not entity.alive:
                        entity.animation_state = "died"
                        defeated_text = language_manager.get("messages.defeated", "Defeated {enemy}!") if language_manager else f"Defeated {enemy_name}!"
                        return defeated_text.replace("{enemy}", enemy_name)
                    else:
                        hit_text = language_manager.get("messages.hit", "Hit {enemy}!") if language_manager else f"Hit {enemy_name}!"
                        return hit_text.replace("{enemy}", enemy_name)
        return None


class InventorySystem:
    """Manages player inventory"""
    
    @staticmethod
    def can_use_item(player: Player, item_name: str) -> bool:
        """Check if player can use an item"""
        if item_name == "sword":
            return player.has_sword
        elif item_name.startswith("key_"):
            return player.has_key(item_name.replace("key_", ""))
        elif item_name in player.quest_items:
            return True
        return False

