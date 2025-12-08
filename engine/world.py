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
        self.exits = {
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
            
    def set_exit(self, direction: str, room_id: str):
        """Set an exit to another room"""
        if direction in self.exits:
            self.exits[direction] = room_id
            
    def get_exit(self, direction: str) -> Optional[str]:
        """Get the room ID for an exit direction"""
        return self.exits.get(direction)
        
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
            
            # Set exits
            for direction, target in room_data.get("exits", {}).items():
                if target:
                    room.set_exit(direction, target)
            
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

