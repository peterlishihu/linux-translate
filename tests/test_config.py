# tests/test_config.py
import os
import json
import tempfile
import pytest
from src.config import Config, ConfigManager


class TestConfig:
    def test_config_default_values(self):
        config = Config()
        assert config.translation['priority'] == ['google', 'baidu', 'youdao', 'argos']
        assert config.ocr['priority'] == ['tesseract', 'cloud']
        assert config.tts['priority'] == ['online', 'offline']

    def test_config_to_dict(self):
        config = Config()
        data = config.to_dict()
        assert 'translation' in data
        assert 'ocr' in data
        assert 'tts' in data


class TestConfigManager:
    def test_load_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'config.json')
            manager = ConfigManager(config_path)
            config = manager.load()
            assert isinstance(config, Config)
            assert config.translation['priority'] == ['google', 'baidu', 'youdao', 'argos']

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'config.json')
            manager = ConfigManager(config_path)
            config = Config()
            config.translation['default_target'] = 'en'
            manager.save(config)

            loaded = manager.load()
            assert loaded.translation['default_target'] == 'en'
