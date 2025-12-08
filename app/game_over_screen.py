"""
Game Over screen
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from engine.language_manager import LanguageManager


class GameOverScreen(QWidget):
    """Game Over screen with Try Again and Main Menu buttons"""
    
    try_again_signal = pyqtSignal()
    main_menu_signal = pyqtSignal()
    
    def __init__(self, language_manager: LanguageManager = None):
        super().__init__()
        self.language_manager = language_manager or LanguageManager()
        self.setStyleSheet("background-color: rgba(42, 42, 58, 230);")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup game over UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Game Over title
        title = QLabel(self.language_manager.get("game.game_over", "GAME OVER"))
        title.setFont(QFont("Arial", 56, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff4444; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Message
        message = QLabel(self.language_manager.get("game.you_died", "You died!"))
        message.setFont(QFont("Arial", 18))
        message.setStyleSheet("color: #cccccc; margin-bottom: 60px;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)
        
        # Try Again button
        try_again_btn = QPushButton(self.language_manager.get("game.try_again", "Try Again"))
        try_again_btn.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        try_again_btn.setFixedSize(300, 60)
        try_again_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a7c59;
                color: white;
                border: 3px solid #5a9c69;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5a9c69;
                border-color: #6abc79;
            }
            QPushButton:pressed {
                background-color: #3a6c49;
            }
        """)
        try_again_btn.clicked.connect(self.try_again_signal.emit)
        layout.addWidget(try_again_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spacing
        layout.addSpacing(20)
        
        # Main Menu button
        main_menu_btn = QPushButton(self.language_manager.get("game.main_menu", "Main Menu"))
        main_menu_btn.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_menu_btn.setFixedSize(300, 60)
        main_menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c6a4a;
                color: white;
                border: 3px solid #9c8a5a;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #9c8a5a;
                border-color: #bcaa6a;
            }
            QPushButton:pressed {
                background-color: #6c5a3a;
            }
        """)
        main_menu_btn.clicked.connect(self.main_menu_signal.emit)
        layout.addWidget(main_menu_btn, alignment=Qt.AlignmentFlag.AlignCenter)

