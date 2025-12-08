"""
Main game window - 1280x720 centered window
"""
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QStackedWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
from app.start_menu import StartMenu
from app.game_over_screen import GameOverScreen
from app.victory_screen import VictoryScreen
from app.game_view import GameView
from app.ui_panels import TopPanel, BottomPanel
from engine.state import GameState
from engine.language_manager import LanguageManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("re-Adventure")
        self.setFixedSize(1280, 720)
        self.setStyleSheet("background-color: #2a2a3a;")
        self.center_window()
        
        # Initialize language manager
        self.language_manager = LanguageManager("english")
        
        # Initialize game state (but don't start game yet)
        self.game_state = None
        
        # Track pressed keys
        self.pressed_keys = set()
        
        # Game loop timer (60 FPS) - starts when game begins
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        
        # Setup UI
        self.setup_ui()
        
    def center_window(self):
        """Center window on screen"""
        screen_geometry = self.screen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def setup_ui(self):
        """Setup main UI layout"""
        # Use stacked widget to switch between menu and game
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create start menu
        self.start_menu = StartMenu(self.language_manager)
        self.start_menu.start_game_signal.connect(self.start_game)
        self.start_menu.exit_game_signal.connect(self.close)
        self.start_menu.language_changed_signal.connect(self.on_language_changed)
        self.stacked_widget.addWidget(self.start_menu)
        
        # Create game over screen
        self.game_over_screen = GameOverScreen(self.language_manager)
        self.game_over_screen.try_again_signal.connect(self.start_game)
        self.game_over_screen.main_menu_signal.connect(self.return_to_menu)
        self.stacked_widget.addWidget(self.game_over_screen)
        
        # Create victory screen
        self.victory_screen = VictoryScreen(self.language_manager)
        self.victory_screen.play_again_signal.connect(self.start_game)
        self.victory_screen.main_menu_signal.connect(self.return_to_menu)
        self.stacked_widget.addWidget(self.victory_screen)
        
        # Create game screen (will be initialized when game starts)
        self.game_widget = None
        
        # Show start menu initially
        self.stacked_widget.setCurrentWidget(self.start_menu)
        
    def start_game(self):
        """Start the game"""
        # Initialize game state with language manager
        self.game_state = GameState()
        self.game_state.language_manager = self.language_manager
        
        # Always recreate game widget with fresh game state
        if self.game_widget is not None:
            self.stacked_widget.removeWidget(self.game_widget)
            self.game_widget.deleteLater()
            
        self.game_widget = QWidget()
        self.game_widget.setStyleSheet("background-color: #2a2a3a;")
        
        layout = QVBoxLayout(self.game_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top panel (health, inventory)
        self.top_panel = TopPanel(self.game_state, self.language_manager)
        layout.addWidget(self.top_panel)
        
        # Game view (main game area)
        self.game_view = GameView(self.game_state)
        layout.addWidget(self.game_view, stretch=1)
        
        # Bottom panel (messages)
        self.bottom_panel = BottomPanel(self.language_manager)
        layout.addWidget(self.bottom_panel)
        
        self.stacked_widget.addWidget(self.game_widget)
        
        # Switch to game screen
        self.stacked_widget.setCurrentWidget(self.game_widget)
        
        # Start game loop
        self.game_timer.start(16)  # ~60 FPS (16ms per frame)
        
    def update_game(self):
        """Main game loop update (called ~60 times per second)"""
        if self.game_state is None:
            return
            
        # Update game state
        self.game_state.update(self.pressed_keys)
        
        # Check for game over
        if self.game_state.game_over:
            self.show_game_over()
            return
            
        # Check for victory
        if self.game_state.game_won:
            self.show_victory()
            return
        
        # Update view
        self.game_view.update_view()
        
        # Update UI panels
        self.top_panel.update_panel()
        
        # Update messages if needed
        if self.game_state.last_message:
            self.bottom_panel.set_message(self.game_state.last_message)
            
    def show_game_over(self):
        """Show game over screen"""
        # Stop game loop
        self.game_timer.stop()
        
        # Clear pressed keys
        self.pressed_keys.clear()
        
        # Stop footsteps if playing
        if self.game_state and self.game_state.audio_manager:
            self.game_state.audio_manager.stop_sound("footsteps")
            # Play game over sound
            self.game_state.audio_manager.play_sound("game_over")
        
        # Switch to game over screen
        self.stacked_widget.setCurrentWidget(self.game_over_screen)
        
    def show_victory(self):
        """Show victory screen"""
        # Stop game loop
        self.game_timer.stop()
        
        # Clear pressed keys
        self.pressed_keys.clear()
        
        # Stop footsteps and play victory sound
        if self.game_state and self.game_state.audio_manager:
            self.game_state.audio_manager.stop_sound("footsteps")
            self.game_state.audio_manager.play_sound("victory")
        
        # Switch to victory screen
        self.stacked_widget.setCurrentWidget(self.victory_screen)
            
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press"""
        key = event.key()
        self.pressed_keys.add(key)
        
        # Handle special keys
        if key == Qt.Key.Key_Escape:
            # If in game, return to menu; if in menu, close
            if self.stacked_widget.currentWidget() == self.game_widget:
                self.return_to_menu()
            else:
                self.close()
            
    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release"""
        key = event.key()
        self.pressed_keys.discard(key)
        
    def return_to_menu(self):
        """Return to start menu"""
        # Stop game loop
        self.game_timer.stop()
        
        # Clear pressed keys
        self.pressed_keys.clear()
        
        # Switch to menu
        self.stacked_widget.setCurrentWidget(self.start_menu)
        
    def on_language_changed(self, language_code: str):
        """Handle language change from menu"""
        # Update main language manager
        self.language_manager.set_language(language_code)
        
        # Update game state if it exists
        if self.game_state:
            self.game_state.language_manager.set_language(language_code)
        
        # Refresh UI panels if game is running
        if self.game_widget:
            self.top_panel.language_manager.set_language(language_code)
            self.bottom_panel.language_manager.set_language(language_code)

