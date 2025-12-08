"""
Game view using QGraphicsView and QGraphicsScene
Handles rendering the game world
"""
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QPen
from engine.sprite_manager import SpriteManager, AnimatedSprite


class GameView(QGraphicsView):
    """Main game rendering view"""
    
    # Logical game resolution (will be scaled to fit window)
    LOGICAL_WIDTH = 640
    LOGICAL_HEIGHT = 480
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        
        # Setup scene
        self.scene = QGraphicsScene(0, 0, self.LOGICAL_WIDTH, self.LOGICAL_HEIGHT)
        self.setScene(self.scene)
        
        # Configure view
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(self.renderHints())
        self.setStyleSheet("background-color: #2a2a3a; border: none;")
        
        # Background
        self.scene.setBackgroundBrush(QBrush(QColor(20, 20, 30)))
        
        # Graphics items
        self.room_items = []
        self.entity_items = {}
        self.entity_sprites = {}  # Track animated sprites
        
        # Sprite manager
        self.sprite_manager = SpriteManager()
        
    def update_view(self):
        """Update the view based on game state"""
        # Clear existing items
        for item in self.room_items:
            self.scene.removeItem(item)
        self.room_items.clear()
        
        # Draw current room
        self.draw_room()
        
        # Update entities
        self.update_entities()
        
    def draw_room(self):
        """Draw the current room"""
        if not self.game_state.current_room:
            return
            
        room = self.game_state.current_room
        
        # Draw room background
        bg_color = self.get_room_color(room.tileset)
        bg_rect = QGraphicsRectItem(0, 0, self.LOGICAL_WIDTH, self.LOGICAL_HEIGHT)
        bg_rect.setBrush(QBrush(bg_color))
        bg_rect.setPen(QPen(Qt.PenStyle.NoPen))
        bg_rect.setZValue(-2)  # Background behind everything
        self.scene.addItem(bg_rect)
        self.room_items.append(bg_rect)
        
        # Draw room borders
        border_pen = QPen(QColor(100, 100, 120), 3)
        border_rect = QGraphicsRectItem(5, 5, self.LOGICAL_WIDTH - 10, self.LOGICAL_HEIGHT - 10)
        border_rect.setPen(border_pen)
        border_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        border_rect.setZValue(-1)  # Borders behind entities but above background
        self.scene.addItem(border_rect)
        self.room_items.append(border_rect)
        
        # Draw exits
        self.draw_exits(room)
        
    def draw_exits(self, room):
        """Draw exit indicators"""
        # Get unlocked doors from game state
        unlocked_doors = getattr(self.game_state, 'unlocked_doors', set())
        
        # Default exit colors (unlocked or no lock)
        exit_pen = QPen(QColor(200, 200, 100), 2)
        exit_brush = QBrush(QColor(150, 150, 80))
        
        # Locked exit colors (red/orange to indicate locked)
        locked_pen = QPen(QColor(200, 100, 50), 3)
        locked_brush = QBrush(QColor(150, 50, 0))
        
        # Helper function to check if exit is locked
        def is_door_unlocked(direction):
            door_key = (room.room_id, direction)
            if door_key in unlocked_doors:
                return True
            if room.is_exit_locked(direction):
                return False
            return True  # Not locked, so unlocked
        
        # North exit
        if room.exits.get("north"):
            is_unlocked = is_door_unlocked("north")
            pen = exit_pen if is_unlocked else locked_pen
            brush = exit_brush if is_unlocked else locked_brush
            exit_rect = QGraphicsRectItem(self.LOGICAL_WIDTH // 2 - 30, 5, 60, 15)
            exit_rect.setPen(pen)
            exit_rect.setBrush(brush)
            exit_rect.setZValue(-1)  # Exits behind entities
            self.scene.addItem(exit_rect)
            self.room_items.append(exit_rect)
            
        # South exit
        if room.exits.get("south"):
            is_unlocked = is_door_unlocked("south")
            pen = exit_pen if is_unlocked else locked_pen
            brush = exit_brush if is_unlocked else locked_brush
            exit_rect = QGraphicsRectItem(self.LOGICAL_WIDTH // 2 - 30, self.LOGICAL_HEIGHT - 20, 60, 15)
            exit_rect.setPen(pen)
            exit_rect.setBrush(brush)
            exit_rect.setZValue(-1)  # Exits behind entities
            self.scene.addItem(exit_rect)
            self.room_items.append(exit_rect)
            
        # East exit
        if room.exits.get("east"):
            is_unlocked = is_door_unlocked("east")
            pen = exit_pen if is_unlocked else locked_pen
            brush = exit_brush if is_unlocked else locked_brush
            exit_rect = QGraphicsRectItem(self.LOGICAL_WIDTH - 20, self.LOGICAL_HEIGHT // 2 - 30, 15, 60)
            exit_rect.setPen(pen)
            exit_rect.setBrush(brush)
            exit_rect.setZValue(-1)  # Exits behind entities
            self.scene.addItem(exit_rect)
            self.room_items.append(exit_rect)
            
        # West exit
        if room.exits.get("west"):
            is_unlocked = is_door_unlocked("west")
            pen = exit_pen if is_unlocked else locked_pen
            brush = exit_brush if is_unlocked else locked_brush
            exit_rect = QGraphicsRectItem(5, self.LOGICAL_HEIGHT // 2 - 30, 15, 60)
            exit_rect.setPen(pen)
            exit_rect.setBrush(brush)
            exit_rect.setZValue(-1)  # Exits behind entities
            self.scene.addItem(exit_rect)
            self.room_items.append(exit_rect)
            
    def update_entities(self):
        """Update all entity graphics"""
        # Build list of all entities to render (room entities + player)
        all_entities = []
        if self.game_state.current_room:
            all_entities.extend(self.game_state.current_room.entities)
        if self.game_state.player:
            all_entities.append(self.game_state.player)
        
        # Remove items for entities that no longer exist
        current_entity_ids = {e.entity_id for e in all_entities}
        for entity_id in list(self.entity_items.keys()):
            if entity_id not in current_entity_ids:
                self.scene.removeItem(self.entity_items[entity_id])
                del self.entity_items[entity_id]
        
        # Update or create items for all entities
        for entity in all_entities:
            self.update_entity_item(entity)
                
    def update_entity_item(self, entity):
        """Update or create graphics item for entity"""
        if entity.entity_id in self.entity_items:
            # Update existing item
            item = self.entity_items[entity.entity_id]
            
            # Update position (center the sprite on entity position)
            sprite_offset = -16  # Half of 32px sprite size
            item.setPos(entity.x + sprite_offset, entity.y + sprite_offset)
            
            # Update sprite animation
            if entity.entity_id in self.entity_sprites:
                animated_sprite = self.entity_sprites[entity.entity_id]
                animated_sprite.set_animation(entity.animation_state)
                animated_sprite.update(0.016)  # ~60 FPS
                frame = animated_sprite.get_current_frame()
                
                # Apply damage flash effect for player - swap to hit sprite
                from engine.entities import Player
                if isinstance(entity, Player) and entity.damage_flash_count > 0 and entity.damage_flash_timer > 0:
                    # Use hit sprite during flash
                    hit_sprite = self.sprite_manager.get_hit_sprite("player")
                    if hit_sprite:
                        item.setPixmap(hit_sprite)
                    else:
                        item.setPixmap(frame)
                else:
                    item.setPixmap(frame)
        else:
            # Create new item
            item = self.create_entity_item(entity)
            if item:
                self.scene.addItem(item)
                self.entity_items[entity.entity_id] = item
            
    def create_entity_item(self, entity):
        """Create graphics item for entity"""
        from engine.entities import Player, Enemy, Item
        
        sprite_offset = -16  # Half of 32px sprite size to center on entity position
        
        if isinstance(entity, Player):
            # Try to use sprite first
            animated_sprite = self.sprite_manager.create_animated_sprite("player")
            if animated_sprite:
                item = QGraphicsPixmapItem(animated_sprite.get_current_frame())
                item.setZValue(10)  # Player on top
                item.setPos(entity.x + sprite_offset, entity.y + sprite_offset)
                self.entity_sprites[entity.entity_id] = animated_sprite
                return item
            else:
                # Fallback to circle
                item = QGraphicsEllipseItem(0, 0, entity.hitbox.width, entity.hitbox.height)
                item.setBrush(QBrush(QColor(50, 150, 255)))
                item.setPen(QPen(QColor(100, 200, 255), 2))
                item.setZValue(10)
                item.setPos(entity.x, entity.y)
                return item
            
        elif isinstance(entity, Enemy):
            # Try to use sprite first
            animated_sprite = self.sprite_manager.create_animated_sprite(entity.subtype)
            if animated_sprite:
                item = QGraphicsPixmapItem(animated_sprite.get_current_frame())
                item.setZValue(5)  # Enemies above background
                item.setPos(entity.x + sprite_offset, entity.y + sprite_offset)
                self.entity_sprites[entity.entity_id] = animated_sprite
                return item
            else:
                # Fallback to circle
                color = self.get_enemy_color(entity.subtype)
                item = QGraphicsEllipseItem(0, 0, entity.hitbox.width, entity.hitbox.height)
                item.setBrush(QBrush(color))
                item.setPen(QPen(color.lighter(150), 2))
                item.setZValue(5)
                item.setPos(entity.x, entity.y)
                return item
            
        elif isinstance(entity, Item):
            # Try to use sprite first
            sprite = self.sprite_manager.get_sprite_sheet(entity.subtype)
            if sprite and not isinstance(sprite, type(None)):
                item = QGraphicsPixmapItem(sprite)
                item.setZValue(3)  # Items above background but below enemies
                item.setPos(entity.x + sprite_offset, entity.y + sprite_offset)
                return item
            else:
                # Fallback to square
                color = self.get_item_color(entity.subtype)
                item = QGraphicsRectItem(0, 0, entity.hitbox.width, entity.hitbox.height)
                item.setBrush(QBrush(color))
                item.setPen(QPen(color.lighter(150), 2))
                item.setZValue(3)
                item.setPos(entity.x, entity.y)
                return item
            
        else:
            # Default gray square
            item = QGraphicsRectItem(0, 0, 16, 16)
            item.setBrush(QBrush(QColor(128, 128, 128)))
            item.setPen(QPen(Qt.PenStyle.NoPen))
            item.setZValue(1)
            item.setPos(entity.x, entity.y)
            return item
            
    def get_room_color(self, tileset):
        """Get background color for tileset"""
        colors = {
            "grasslands": QColor(60, 100, 60),
            "castle": QColor(80, 80, 90),
            "dungeon": QColor(40, 40, 50),
            "forest": QColor(30, 60, 30),
            "labyrinth": QColor(60, 50, 40)
        }
        return colors.get(tileset, QColor(50, 50, 60))
        
    def get_enemy_color(self, subtype):
        """Get color for enemy type"""
        colors = {
            "dragon_red": QColor(200, 50, 50),
            "dragon_yellow": QColor(200, 200, 50),
            "dragon_green": QColor(50, 200, 50),
            "bat": QColor(100, 50, 150)
        }
        return colors.get(subtype, QColor(150, 50, 50))
        
    def get_item_color(self, subtype):
        """Get color for item type"""
        colors = {
            "key_gold": QColor(255, 215, 0),
            "key_silver": QColor(192, 192, 192),
            "sword": QColor(180, 180, 200),
            "chalice": QColor(255, 215, 0)
        }
        return colors.get(subtype, QColor(200, 200, 100))
        
    def resizeEvent(self, event):
        """Handle window resize - scale to fit"""
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

