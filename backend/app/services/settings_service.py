import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SettingsService:
    '''Service for managing user settings'''
    
    def __init__(self, settings_file: str = "./settings.json"):
        self.settings_file = Path(settings_file)
        self.default_settings = {
            "llm_provider": "groq",
            "llm_model": {
                "groq": "llama-3.3-70b-versatile",
                "gemini": "models/gemini-2.5-flash",
                "openrouter": "qwen/qwen-2.5-32b:free",
                "ollama": "tinyllama"
            },
            "theme": "dark",
            "slide_count": 10,
            "audience": "general",
            "tone": "educational",
            "animation_quality": "medium",
            "auto_save": True,
            "show_timeline": True,
            "enable_animations": True,
            "enable_diagrams": True
        }
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        '''Load settings from file or return defaults'''
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    settings = self.default_settings.copy()
                    settings.update(loaded)
                    return settings
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}")
        return self.default_settings.copy()
    
    def _save_settings(self):
        '''Save settings to file'''
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get_settings(self) -> Dict[str, Any]:
        '''Get all settings'''
        return self.settings.copy()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        '''Get a specific setting'''
        return self.settings.get(key, default)
    
    def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        '''Update settings with new values'''
        valid_keys = set(self.default_settings.keys())
        for key, value in updates.items():
            if key in valid_keys:
                # Validate specific settings
                if key == "llm_provider" and value not in ["groq", "gemini", "openrouter", "ollama"]:
                    continue
                if key == "theme" and value not in ["dark", "light", "system"]:
                    continue
                if key == "animation_quality" and value not in ["low", "medium", "high", "ultra"]:
                    continue
                if key == "audience" and value not in ["general", "beginner", "intermediate", "expert"]:
                    continue
                if key == "tone" and value not in ["professional", "educational", "casual", "persuasive"]:
                    continue
                if key == "slide_count" and not (5 <= value <= 20):
                    continue
                
                self.settings[key] = value
                logger.info(f"Setting updated: {key} = {value}")
        
        self._save_settings()
        return self.settings.copy()
    
    def reset_settings(self) -> Dict[str, Any]:
        '''Reset settings to defaults'''
        self.settings = self.default_settings.copy()
        self._save_settings()
        return self.settings.copy()

# Singleton instance
settings_service = SettingsService()
