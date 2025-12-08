"""
World and Room management
"""
from typing import Dict, List, Optional
from engine.entities import Entity, Player, Enemy, Item, Hazard


class Room:
    """A single room in the game world"""
    
    def __init__(self, room_id: str, name: str, tileset: str = "grasslands"):
        self.room_id = room_id
        self.name = name
        self.tileset = tileset
        # Exits can be either a string (room_id) or a dict with room, locked, and key
        self.exits = {
            "north": None,
            "south": None,
            "east": None,
            "west": None
        }
        # Exit metadata: {direction: {"locked": bool, "key": str}}
        self.exit_metadata = {
            "north": None,
            "south": None,
            "east": None,
            "west": None
        }
        self.entities: List[Entity] = []
        self.player_spawn = (320, 240)  # Default spawn position
        
    def add_entity(self, entity: Entity):
        """Add an entity to this room"""
        self.entities.append(entity)
        
    def remove_entity(self, entity: Entity):
        """Remove an entity from this room"""
        if entity in self.entities:
            self.entities.remove(entity)
            
    def set_exit(self, direction: str, room_id: str, locked: bool = False, key_type: Optional[str] = None):
        """Set an exit to another room, optionally locked"""
        if direction in self.exits:
            self.exits[direction] = room_id
            if locked and key_type:
                self.exit_metadata[direction] = {"locked": True, "key": key_type}
            else:
                self.exit_metadata[direction] = None
                
    def get_exit(self, direction: str) -> Optional[str]:
        """Get the room ID for an exit direction"""
        return self.exits.get(direction)
        
    def is_exit_locked(self, direction: str) -> bool:
        """Check if an exit is locked"""
        metadata = self.exit_metadata.get(direction)
        if metadata:
            return metadata.get("locked", False)
        return False
        
    def get_exit_key(self, direction: str) -> Optional[str]:
        """Get the key type required for a locked exit"""
        metadata = self.exit_metadata.get(direction)
        if metadata:
            return metadata.get("key")
        return None
        
    def unlock_exit(self, direction: str):
        """Unlock an exit"""
        if direction in self.exit_metadata:
            self.exit_metadata[direction] = None
        
    def cleanup_dead_entities(self):
        """Remove dead entities from the room"""
        self.entities = [e for e in self.entities if e.alive]


class World:
    """Game world containing all rooms"""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.starting_room_id = None
        
    def add_room(self, room: Room):
        """Add a room to the world"""
        self.rooms[room.room_id] = room
        if self.starting_room_id is None:
            self.starting_room_id = room.room_id
            
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID"""
        return self.rooms.get(room_id)
        
    def set_starting_room(self, room_id: str):
        """Set the starting room"""
        if room_id in self.rooms:
            self.starting_room_id = room_id
            
    def load_from_json(self, data: dict):
        """Load world from JSON data"""
        for room_data in data.get("rooms", []):
            room = Room(
                room_id=room_data["id"],
                name=room_data.get("name", room_data["id"]),
                tileset=room_data.get("tileset", "grasslands")
            )
            
            # Set exits (support both simple string format and locked door format)
            for direction, exit_data in room_data.get("exits", {}).items():
                if exit_data:
                    if isinstance(exit_data, dict):
                        # New format: {"room": "room_id", "locked": true, "key": "gold"}
                        room_id = exit_data.get("room")
                        locked = exit_data.get("locked", False)
                        key_type = exit_data.get("key")
                        if room_id:
                            room.set_exit(direction, room_id, locked, key_type)
                    else:
                        # Old format: just a string room_id
                        room.set_exit(direction, exit_data)
            
            # Create entities
            for entity_data in room_data.get("entities", []):
                entity = self.create_entity_from_data(entity_data)
                if entity:
                    if entity_data["type"] == "player_spawn":
                        room.player_spawn = (entity_data["x"], entity_data["y"])
                    else:
                        room.add_entity(entity)
            
            self.add_room(room)
            
        # Set starting room if specified
        if "starting_room" in data:
            self.set_starting_room(data["starting_room"])
            
    def create_entity_from_data(self, data: dict) -> Optional[Entity]:
        """Create an entity from JSON data"""
        entity_type = data.get("type")
        x = data.get("x", 0)
        y = data.get("y", 0)
        
        if entity_type == "player_spawn":
            return None  # Handled separately
            
        elif entity_type == "enemy":
            return Enemy(x, y, data.get("subtype", "dragon_red"))
            
        elif entity_type == "item":
            return Item(x, y, data.get("subtype", "key_gold"))
            
        elif entity_type == "hazard":
            return Hazard(x, y, data.get("subtype", "spike"))
            
        return None

