"""
Language/Translation Manager
Handles loading and providing translations
"""
import json
import os
from typing import Dict


class LanguageManager:
    """Manages game translations"""
    
    def __init__(self, language: str = None):
        # Get settings file path
        base_path = os.path.join(os.path.dirname(__file__), "..")
        self.settings_file = os.path.join(base_path, "data", "language_settings.json")
        
        # Load saved language preference or use default
        if language is None:
            language = self.load_saved_language()
        
        self.current_language = language
        self.translations: Dict[str, str] = {}
        self.load_language(language)
        
    def load_language(self, language: str):
        """Load a language file"""
        self.current_language = language
        
        # Get path to language files
        base_path = os.path.join(os.path.dirname(__file__), "..", "data", "languages")
        lang_file = os.path.join(base_path, f"{language}.json")
        
        try:
            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            else:
                # Fallback to English if language file not found
                if language != "english":
                    self.load_language("english")
                else:
                    self.translations = {}
        except Exception as e:
            print(f"Error loading language {language}: {e}")
            if language != "english":
                self.load_language("english")
                
    def get(self, key: str, default: str = None) -> str:
        """Get a translation by key (supports nested keys like 'menu.title')"""
        keys = key.split('.')
        value = self.translations
        
        try:
            for k in keys:
                value = value[k]
            return value if isinstance(value, str) else (default or key)
        except (KeyError, TypeError):
            return default or key
        
    def t(self, key: str, default: str = None) -> str:
        """Shortcut for get()"""
        return self.get(key, default)
        
    def set_language(self, language: str):
        """Change the current language"""
        self.load_language(language)
        self.save_language_preference(language)
        
    def load_saved_language(self) -> str:
        """Load saved language preference from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get("language", "english")
        except Exception:
            pass
        return "english"
        
    def save_language_preference(self, language: str):
        """Save language preference to file"""
        try:
            # Ensure data directory exists
            settings_dir = os.path.dirname(self.settings_file)
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir, exist_ok=True)
                
            settings = {"language": language}
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save language preference: {e}")
        
    def get_available_languages(self) -> list:
        """Get list of available language files"""
        base_path = os.path.join(os.path.dirname(__file__), "..", "data", "languages")
        languages = []
        
        if os.path.exists(base_path):
            for filename in os.listdir(base_path):
                if filename.endswith('.json'):
                    lang_name = filename[:-5]  # Remove .json
                    languages.append(lang_name)
                    
        return sorted(languages) if languages else ["english"]

