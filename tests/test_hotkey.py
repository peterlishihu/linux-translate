import pytest
from unittest.mock import patch, MagicMock
from src.services.hotkey import HotkeyManager


class TestHotkeyManager:
    def test_init(self):
        manager = HotkeyManager()
        assert manager.shortcuts == {}

    def test_register_shortcut(self):
        manager = HotkeyManager()
        callback = MagicMock()

        with patch.object(manager, '_start_listener'):
            manager.register('<ctrl>+<alt>+t', callback)
            assert '<ctrl>+<alt>+t' in manager.shortcuts

    def test_unregister_shortcut(self):
        manager = HotkeyManager()
        callback = MagicMock()

        with patch.object(manager, '_start_listener'):
            manager.register('<ctrl>+<alt>+t', callback)
            manager.unregister('<ctrl>+<alt>+t')
            assert '<ctrl>+<alt>+t' not in manager.shortcuts
