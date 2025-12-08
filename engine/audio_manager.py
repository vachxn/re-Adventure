"""
Audio management for sound effects and music
"""
import os
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl


class SoundEffect:
    """Wrapper for sound effect using QMediaPlayer"""
    
    def __init__(self, file_path, volume=0.5, loop=False):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.audio_output.setVolume(volume)
        self.is_looping = loop
        if loop:
            self.player.setLoops(QMediaPlayer.Loops.Infinite)
        
    def play(self):
        """Play the sound"""
        if not self.is_looping:
            # Reset to beginning for one-shot sounds
            self.player.setPosition(0)
        self.player.play()
        
    def stop(self):
        """Stop the sound"""
        self.player.stop()
        
    def is_playing(self):
        """Check if sound is currently playing"""
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        
    def setVolume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.audio_output.setVolume(volume)


class AudioManager:
    """Manages game audio"""
    
    def __init__(self):
        self.sound_effects = {}
        self.music_player = None
        self.music_audio_output = None
        self.enabled = True
        
        # Load sound effects
        self.load_sounds()
        
    def load_sounds(self):
        """Load all sound effects"""
        # Get base path for audio
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")
        
        # Ensure directory exists
        os.makedirs(base_path, exist_ok=True)
        
        # Define sound files (filename, loop)
        sound_files = {
            "item_collected": ("item-collected-1-367087.mp3", False),
            "victory": ("item-found-87528.mp3", False),
            "sword_hit": ("violent-sword-slice-2-393841.mp3", False),
            "footsteps": ("8-bit-grass-footsteps-2-408574.mp3", True),  # Looping footsteps
            "game_over": ("dead-8bit-41400.mp3", False),
            "player_hurt": ("retro-hurt-1-236672.mp3", False),
            # Add more sounds here as needed
        }
        
        # Load each sound effect
        for name, (filename, loop) in sound_files.items():
            path = os.path.abspath(os.path.join(base_path, filename))
            if os.path.exists(path):
                try:
                    sound = SoundEffect(path, volume=0.3 if loop else 0.5, loop=loop)
                    self.sound_effects[name] = sound
                    print(f"Loaded sound: {name} (loop={loop}) from {path}")
                except Exception as e:
                    print(f"Error loading sound {name}: {e}")
            else:
                print(f"Warning: Sound file not found: {path}")
                
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.enabled:
            return
            
        if sound_name in self.sound_effects:
            sound = self.sound_effects[sound_name]
            sound.play()
        else:
            print(f"Sound not found: {sound_name}")
            
    def stop_sound(self, sound_name):
        """Stop a sound effect"""
        if sound_name in self.sound_effects:
            sound = self.sound_effects[sound_name]
            sound.stop()
            
    def is_sound_playing(self, sound_name):
        """Check if a sound is currently playing"""
        if sound_name in self.sound_effects:
            return self.sound_effects[sound_name].is_playing()
        return False
            
    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)"""
        for sound in self.sound_effects.values():
            sound.setVolume(volume)
            
    def enable_audio(self, enabled):
        """Enable or disable audio"""
        self.enabled = enabled
        
    def play_music(self, music_file, loop=True):
        """Play background music"""
        if not self.enabled:
            return
            
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")
        path = os.path.abspath(os.path.join(base_path, music_file))
        
        if not os.path.exists(path):
            print(f"Music file not found: {path}")
            return
            
        # Create player if needed
        if self.music_player is None:
            self.music_player = QMediaPlayer()
            self.music_audio_output = QAudioOutput()
            self.music_player.setAudioOutput(self.music_audio_output)
            
        # Set source and play
        self.music_player.setSource(QUrl.fromLocalFile(path))
        
        if loop:
            self.music_player.setLoops(QMediaPlayer.Loops.Infinite)
            
        self.music_player.play()
        
    def stop_music(self):
        """Stop background music"""
        if self.music_player:
            self.music_player.stop()

