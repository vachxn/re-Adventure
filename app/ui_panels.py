"""
UI Panels for HUD elements
Top panel: health, inventory
Bottom panel: messages
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from engine.language_manager import LanguageManager


class TopPanel(QWidget):
    """Top panel showing health and inventory"""
    
    def __init__(self, game_state, language_manager: LanguageManager = None):
        super().__init__()
        self.game_state = game_state
        self.language_manager = language_manager or LanguageManager()
        self.setFixedHeight(60)
        self.setStyleSheet("background-color: #2a2a3a; color: white;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Room name
        self.room_label = QLabel(f"{self.language_manager.get('game.room', 'Room')}: Unknown")
        self.room_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.room_label)
        
        layout.addStretch()
        
        # Health display
        self.health_label = QLabel("❤ ❤ ❤")
        self.health_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.health_label)
        
        layout.addStretch()
        
        # Inventory display
        self.inventory_label = QLabel(f"{self.language_manager.get('game.inventory', 'Inventory')}: ")
        self.inventory_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.inventory_label)
        
    def update_panel(self):
        """Update panel display"""
        # Update room name
        if self.game_state.current_room:
            room_text = self.language_manager.get("game.room", "Room")
            self.room_label.setText(f"{room_text}: {self.game_state.current_room.name}")
        
        # Update health
        if self.game_state.player:
            hearts = "❤ " * self.game_state.player.health
            empty_hearts = "♡ " * (self.game_state.player.max_health - self.game_state.player.health)
            self.health_label.setText(hearts + empty_hearts)
        
        # Update inventory
        if self.game_state.player:
            inv_items = []
            if self.game_state.player.has_sword:
                inv_items.append("⚔️ " + self.language_manager.get("messages.found_sword", "Sword").replace("Found ", "").replace("!", ""))
            for key in self.game_state.player.keys:
                inv_items.append(f"🔑 {key}")
            for item in self.game_state.player.quest_items:
                inv_items.append(f"✨ {item}")
                
            inventory_text = self.language_manager.get("game.inventory", "Inventory")
            if inv_items:
                self.inventory_label.setText(f"{inventory_text}: " + ", ".join(inv_items))
            else:
                empty_text = self.language_manager.get("game.inventory_empty", "Empty")
                self.inventory_label.setText(f"{inventory_text}: {empty_text}")


class BottomPanel(QWidget):
    """Bottom panel showing game messages"""
    
    def __init__(self, language_manager: LanguageManager = None):
        super().__init__()
        self.language_manager = language_manager or LanguageManager()
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2a2a3a; color: #aaffaa;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        welcome_text = self.language_manager.get("game.welcome", "Welcome to re-Adventure!")
        self.message_label = QLabel(welcome_text)
        self.message_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.message_label)
        
    def set_message(self, message):
        """Set the current message"""
        self.message_label.setText(message)

