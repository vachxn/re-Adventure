"""
Start menu screen
"""
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from engine.language_manager import LanguageManager


class StartMenu(QWidget):
    """Start menu with Start Game and Exit buttons"""
    
    start_game_signal = pyqtSignal()
    exit_game_signal = pyqtSignal()
    language_changed_signal = pyqtSignal(str)  # Emits language code when changed
    
    def __init__(self, language_manager: LanguageManager = None):
        super().__init__()
        self.language_manager = language_manager or LanguageManager()
        self.flag_buttons = {}  # Initialize before setup_ui
        self.setStyleSheet("background-color: #2a2a3a;")
        self.setup_ui()
        
    def change_language(self, language_code: str):
        """Change the game language"""
        self.language_manager.set_language(language_code)
        self.language_changed_signal.emit(language_code)
        # Refresh UI with new language
        self.refresh_ui()
        
    def refresh_ui(self):
        """Refresh all UI text with current language"""
        # Update labels
        self.title_label.setText(self.language_manager.get("menu.title", "re-Adventure"))
        self.subtitle_label.setText(self.language_manager.get("menu.subtitle", "A re-imagining of the classic \"Adventure\" game"))
        self.instructions_label.setText(self.language_manager.get("menu.controls", "Controls: WASD/Arrows to move • Space/E to attack • ESC to quit"))
        self.objective_label.setText(self.language_manager.get("menu.objective", "Objective: Find the Enchanted Chalice!"))
        
        # Update buttons
        self.start_btn.setText(self.language_manager.get("menu.start_game", "Start Game"))
        self.exit_btn.setText(self.language_manager.get("menu.exit", "Exit"))
        
        # Update flag button highlights
        for lang_code, btn in self.flag_buttons.items():
            if lang_code == self.language_manager.current_language:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4a7c59;
                        border: 2px solid #5a9c69;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #5a9c69;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a4a;
                        border: 2px solid #4a4a5a;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #4a4a5a;
                        border-color: #5a5a6a;
                    }
                """)
        
    def setup_ui(self):
        """Setup menu UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        self.title_label = QLabel(self.language_manager.get("menu.title", "re-Adventure"))
        self.title_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #ffdd44; margin-bottom: 20px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel(self.language_manager.get("menu.subtitle", "A re-imagining of the classic \"Adventure\" game"))
        self.subtitle_label.setFont(QFont("Arial", 14))
        self.subtitle_label.setStyleSheet("color: #aaaaaa; margin-bottom: 60px;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle_label)
        
        # Start Game button
        self.start_btn = QPushButton(self.language_manager.get("menu.start_game", "Start Game"))
        self.start_btn.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.start_btn.setFixedSize(300, 60)
        self.start_btn.setStyleSheet("""
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
        self.start_btn.clicked.connect(self.start_game_signal.emit)
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spacing
        layout.addSpacing(20)
        
        # Exit button
        self.exit_btn = QPushButton(self.language_manager.get("menu.exit", "Exit"))
        self.exit_btn.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.exit_btn.setFixedSize(300, 60)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c4a4a;
                color: white;
                border: 3px solid #9c5a5a;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #9c5a5a;
                border-color: #bc6a6a;
            }
            QPushButton:pressed {
                background-color: #6c3a3a;
            }
        """)
        self.exit_btn.clicked.connect(self.exit_game_signal.emit)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Instructions
        layout.addSpacing(60)
        self.instructions_label = QLabel(self.language_manager.get("menu.controls", "Controls: WASD/Arrows to move • Space/E to attack • ESC to quit"))
        self.instructions_label.setFont(QFont("Arial", 11))
        self.instructions_label.setStyleSheet("color: #888888;")
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instructions_label)
        
        # Objective
        self.objective_label = QLabel(self.language_manager.get("menu.objective", "Objective: Find the Enchanted Chalice!"))
        self.objective_label.setFont(QFont("Arial", 11))
        self.objective_label.setStyleSheet("color: #888888;")
        self.objective_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.objective_label)
        
        # Language selection flags
        layout.addSpacing(20)  # 2 line breaks worth of spacing
        
        flags_label = QLabel("Language / Langue / Sprache / Idioma / Språk / 言語 / 语言:")
        flags_label.setFont(QFont("Arial", 10))
        flags_label.setStyleSheet("color: #666666;")
        flags_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(flags_label)
        
        flags_layout = QHBoxLayout()
        flags_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flags_layout.setSpacing(10)
        
        # Language flags mapping (country codes)
        self.language_flags = {
            "english": "gb",
            "french": "fr",
            "german": "de",
            "spanish": "es",
            "swedish": "se",
            "japanese": "jp",
            "chinese": "cn"
        }
        
        # Get path to flag images
        base_path = os.path.join(os.path.dirname(__file__), "..")
        flags_path = os.path.join(base_path, "assets", "flags")
        
        self.flag_buttons = {}
        for lang_code, country_code in self.language_flags.items():
            flag_btn = QPushButton()
            flag_btn.setFixedSize(80, 30)
            flag_btn.setToolTip(lang_code.capitalize())
            
            # Load flag image
            flag_file = os.path.join(flags_path, f"{country_code}.png")
            if os.path.exists(flag_file):
                pixmap = QPixmap(flag_file)
                # Scale to fit button (80x30) while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(80, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon = QIcon(scaled_pixmap)
                flag_btn.setIcon(icon)
                flag_btn.setIconSize(scaled_pixmap.size())
            else:
                # Fallback to text if image not found
                flag_btn.setText(country_code.upper())
                flag_btn.setFont(QFont("Arial", 10))
            
            # Highlight current language
            if lang_code == self.language_manager.current_language:
                flag_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4a7c59;
                        border: 2px solid #5a9c69;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #5a9c69;
                    }
                """)
            else:
                flag_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a4a;
                        border: 2px solid #4a4a5a;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #4a4a5a;
                        border-color: #5a5a6a;
                    }
                """)
            
            flag_btn.clicked.connect(lambda checked, lang=lang_code: self.change_language(lang))
            flags_layout.addWidget(flag_btn)
            self.flag_buttons[lang_code] = flag_btn
        
        layout.addLayout(flags_layout)

