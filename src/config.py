# src/config.py
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


DEFAULT_CONFIG = {
    'translation': {
        'priority': ['google', 'baidu', 'youdao', 'argos'],
        'default_source': 'auto',
        'default_target': 'zh',
        'api_keys': {
            'baidu': {'appid': '', 'key': ''},
            'youdao': {'appkey': '', 'appsecret': ''}
        }
    },
    'ocr': {
        'priority': ['tesseract', 'cloud'],
        'api_keys': {
            'baidu': {'appid': '', 'key': ''}
        }
    },
    'tts': {
        'priority': ['online', 'offline'],
        'speed': 1.0,
        'volume': 1.0
    },
    'hotkeys': {
        'translate_selection': '<Ctrl><Alt>t',
        'ocr_translate': '<Ctrl><Alt>o',
        'show_float_window': '<Ctrl><Alt>f'
    },
    'ui': {
        'follow_mouse': True,
        'float_window_visible': True,
        'theme': 'system'
    }
}


class Config:
    def __init__(self, data: Dict[str, Any] = None):
        if data is None:
            data = DEFAULT_CONFIG.copy()
        self.translation = data.get('translation', DEFAULT_CONFIG['translation'].copy())
        self.ocr = data.get('ocr', DEFAULT_CONFIG['ocr'].copy())
        self.tts = data.get('tts', DEFAULT_CONFIG['tts'].copy())
        self.hotkeys = data.get('hotkeys', DEFAULT_CONFIG['hotkeys'].copy())
        self.ui = data.get('ui', DEFAULT_CONFIG['ui'].copy())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'translation': self.translation,
            'ocr': self.ocr,
            'tts': self.tts,
            'hotkeys': self.hotkeys,
            'ui': self.ui
        }


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_dir = os.path.expanduser('~/.config/linux-translate')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'config.json')
        self.config_path = config_path

    def load(self) -> Config:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Config(data)
        return Config()

    def save(self, config: Config):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
