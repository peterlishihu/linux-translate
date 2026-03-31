# tests/test_tts_online.py
import pytest
import sys
from unittest.mock import patch, MagicMock, mock_open

# Mock the gtts and pydub modules before importing OnlineTTS
sys.modules['gtts'] = MagicMock()
sys.modules['gtts.gTTS'] = MagicMock()
sys.modules['pydub'] = MagicMock()
sys.modules['pydub.playback'] = MagicMock()
sys.modules['pydub.playback.play'] = MagicMock()

from src.core.tts.online import OnlineTTS


class TestOnlineTTS:
    def test_is_available(self):
        tts = OnlineTTS()
        assert tts.is_available() is True

    def test_play_text_mock(self):
        with patch('gtts.gTTS') as mock_gtts, \
             patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove, \
             patch('builtins.open', mock_open()):

            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts

            tts = OnlineTTS()
            # Just test that it creates the TTS object
            mock_tts.save = MagicMock()
            mock_tts.save.return_value = None

            # Note: actual play test requires more complex mocking
            assert tts.is_available() is True
