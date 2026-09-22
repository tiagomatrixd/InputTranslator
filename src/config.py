import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "hotkey": "alt+t",
    "source_lang": "auto",
    "target_lang": "en",
    "auto_send": True,
    "paste_delay_ms": 100,
    "close_on_send": True,
    "realtime_translation": True,
    "start_with_windows": False,
    "window_width": 620,
    "window_height": 260
}

SUPPORTED_LANGUAGES = {
    "auto": "Detectar Automaticamente",
    "en": "Inglês (English)",
    "pt": "Português",
    "es": "Espanhol (Español)",
    "fr": "Francês (Français)",
    "de": "Alemão (Deutsch)",
    "it": "Italiano",
    "ru": "Russo (Русский)",
    "ja": "Japonês (日本語)",
    "ko": "Coreano (한국어)",
    "zh-CN": "Chinês Simplificado (中文)",
    "ar": "Árabe (العربية)",
    "tr": "Turco (Türkçe)",
    "nl": "Holandês (Nederlands)",
    "pl": "Polonês (Polski)",
    "uk": "Ucraniano (Українська)",
    "hi": "Hindi (हिन्दी)",
    "id": "Indonésio (Bahasa Indonesia)"
}

class ConfigManager:
    def __init__(self):
        self.app_dir = Path(os.environ.get("APPDATA", Path.home())) / "InputTranslator"
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.app_dir / "config.json"
        self.data = self.load()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge with defaults
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(data)
                    return merged
            except Exception as e:
                print(f"Erro ao carregar configuracoes: {e}")
        return DEFAULT_CONFIG.copy()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuracoes: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()

config = ConfigManager()
