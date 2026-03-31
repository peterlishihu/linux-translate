import threading
from typing import Callable, Dict


class HotkeyManager:
    def __init__(self):
        self.shortcuts: Dict[str, Callable] = {}
        self._listener = None
        self._running = False

    def register(self, shortcut: str, callback: Callable):
        """Register a global hotkey

        Args:
            shortcut: Hotkey combination like '<ctrl>+<alt>+t'
            callback: Function to call when hotkey is pressed
        """
        self.shortcuts[shortcut] = callback
        if not self._running:
            self._start_listener()

    def unregister(self, shortcut: str):
        """Unregister a hotkey"""
        if shortcut in self.shortcuts:
            del self.shortcuts[shortcut]

    def stop(self):
        """Stop the hotkey listener"""
        self._running = False
        if self._listener:
            self._listener.stop()

    def _start_listener(self):
        """Start the global hotkey listener"""
        try:
            from pynput import keyboard

            def on_activate(shortcut):
                callback = self.shortcuts.get(shortcut)
                if callback:
                    callback()

            # Create hotkey combinations
            hotkeys = {}
            for shortcut, callback in self.shortcuts.items():
                hotkeys[shortcut] = lambda s=shortcut: on_activate(s)

            self._listener = keyboard.GlobalHotKeys(hotkeys)
            self._listener.start()
            self._running = True

        except ImportError:
            print("Warning: pynput not available, hotkeys disabled")
        except Exception as e:
            print(f"Warning: Failed to start hotkey listener: {e}")

    def is_available(self) -> bool:
        """Check if hotkey support is available"""
        try:
            from pynput import keyboard
            return True
        except ImportError:
            return False
