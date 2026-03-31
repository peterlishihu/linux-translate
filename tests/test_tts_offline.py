import pytest
from unittest.mock import patch, MagicMock
from src.core.tts.offline import OfflineTTS


class TestOfflineTTS:
    def test_is_available_with_pyttsx3(self):
        with patch.dict('sys.modules', {'pyttsx3': MagicMock()}):
            tts = OfflineTTS()
            assert tts.is_available() is True

    def test_is_available_without_pyttsx3(self):
        with patch.dict('sys.modules', {'pyttsx3': None}):
            tts = OfflineTTS()
            assert tts.is_available() is False

    def test_name(self):
        tts = OfflineTTS()
        assert tts.name == "offline"
