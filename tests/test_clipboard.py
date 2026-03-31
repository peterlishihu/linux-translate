# tests/test_clipboard.py
import pytest
from unittest.mock import patch, MagicMock
from src.utils.clipboard import ClipboardManager


class TestClipboardManager:
    def test_get_text(self):
        with patch('src.utils.clipboard.shutil.which', return_value='/usr/bin/wl-paste'):
            with patch('src.utils.clipboard.subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(stdout='test text', returncode=0)
                result = ClipboardManager.get_text()
                assert result == 'test text'

    def test_get_text_empty(self):
        with patch('src.utils.clipboard.shutil.which', return_value='/usr/bin/wl-paste'):
            with patch('src.utils.clipboard.subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(stdout='', returncode=0)
                result = ClipboardManager.get_text()
                assert result == ''

    def test_set_text(self):
        with patch('src.utils.clipboard.shutil.which', return_value='/usr/bin/wl-copy'):
            with patch('src.utils.clipboard.subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = ClipboardManager.set_text('test text')
                assert result is True
