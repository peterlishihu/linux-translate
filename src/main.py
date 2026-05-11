# src/main.py
import sys
import os
import signal
import threading
from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, Qt, QMetaObject, Q_ARG
from PyQt6.QtGui import QAction

from src.gui.main_window import MainWindow
from src.gui.float_window import FloatWindow
from src.gui.result_popup import ResultPopup
from src.gui.history_dialog import HistoryDialog
from src.gui.settings_dialog import SettingsDialog
from src.config import ConfigManager
from src.db.history import HistoryManager
from src.core.translation import (
    GoogleTranslator, BaiduTranslator, YoudaoTranslator, ArgosTranslator,
    TranslationResult
)
from src.core.tts import OfflineTTS, OnlineTTS
from src.core.ocr import TesseractOCR
from src.utils.clipboard import ClipboardManager
from src.utils.screenshot import ScreenshotManager
from src.services.hotkey import HotkeyManager


class HotkeyBridge(QObject):
    """Bridge to marshal hotkey callbacks from pynput thread to Qt main thread."""
    translate_selection = pyqtSignal()
    ocr_translate = pyqtSignal()
    toggle_float = pyqtSignal()


class TranslationWorker(QObject):
    """Worker for async translation in a separate thread."""
    finished = pyqtSignal(object, str)  # (TranslationResult, engine_name)
    error = pyqtSignal(str)

    def __init__(self, translators, priority, text, source_lang, target_lang):
        super().__init__()
        self.translators = translators
        self.priority = priority
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang

    def run(self):
        for engine_name in self.priority:
            if engine_name in self.translators:
                try:
                    result = self.translators[engine_name].translate(
                        self.text, self.source_lang, self.target_lang
                    )
                    self.finished.emit(result, engine_name)
                    return
                except Exception as e:
                    print(f"Translation failed with {engine_name}: {e}")
                    continue
        self.error.emit("所有翻译引擎均失败")


class TranslatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()
        self.history = HistoryManager()

        # Initialize translators
        self.translators = {}
        self._init_translators()

        # Initialize TTS
        self._init_tts()

        # Initialize OCR
        self.ocr = TesseractOCR()

        # Create GUI components
        self.main_window = MainWindow()
        self.float_window = FloatWindow()
        self.result_popup = ResultPopup()

        # Setup hotkey bridge for thread safety
        self.hotkey_bridge = HotkeyBridge()
        self.hotkey_manager = HotkeyManager()

        # Connect signals
        self._connect_signals()

        # Setup tray menu extensions
        self._setup_tray_menu()

        # Register hotkeys
        self._register_hotkeys()

        # Setup signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)

        # Track active workers to prevent GC
        self._workers = []

    def _init_translators(self):
        """Initialize all translation engines."""
        # Google Translator (always available, no key needed)
        google = GoogleTranslator()
        if google.is_available():
            self.translators['google'] = google

        # Baidu Translator
        baidu_config = self.config.translation.get('api_keys', {}).get('baidu', {})
        if baidu_config.get('appid') and baidu_config.get('key'):
            baidu = BaiduTranslator(
                appid=baidu_config['appid'],
                key=baidu_config['key']
            )
            if baidu.is_available():
                self.translators['baidu'] = baidu

        # Youdao Translator
        youdao_config = self.config.translation.get('api_keys', {}).get('youdao', {})
        if youdao_config.get('appkey') and youdao_config.get('appsecret'):
            youdao = YoudaoTranslator(
                appkey=youdao_config['appkey'],
                appsecret=youdao_config['appsecret']
            )
            if youdao.is_available():
                self.translators['youdao'] = youdao

        # Argos Offline Translator
        argos = ArgosTranslator()
        if argos.is_available():
            self.translators['argos'] = argos
        else:
            # Try installing models in background on first run
            self._argos = argos
            thread = threading.Thread(target=self._setup_argos, daemon=True)
            thread.start()

    def _setup_argos(self):
        """Background setup for Argos offline translation models."""
        try:
            if self._argos.ensure_models_installed():
                self.translators['argos'] = self._argos
                print("Argos offline translation models ready")
        except Exception as e:
            print(f"Argos setup failed: {e}")

    def _init_tts(self):
        """Initialize TTS engine (prefer offline)."""
        tts_speed = self.config.tts.get('speed', 1.0)
        rate = int(tts_speed * 150)

        self.tts = OfflineTTS(rate=rate)
        if not self.tts.is_available():
            self.tts = OnlineTTS(speed=tts_speed)

    def _connect_signals(self):
        """Connect all signals between components."""
        # Main window translation
        self.main_window.translate_requested.connect(self._on_translate)

        # Main window TTS buttons
        self.main_window.play_source_btn.clicked.connect(self._on_speak_source)
        self.main_window.play_translated_btn.clicked.connect(self._on_speak_translated)

        # Float window translation
        self.float_window.translate_requested.connect(self._on_float_translate)

        # Result popup actions
        self.result_popup.copy_requested.connect(ClipboardManager.set_text)
        self.result_popup.speak_requested.connect(self._on_speak)

        # Hotkey bridge signals (thread-safe)
        self.hotkey_bridge.translate_selection.connect(self._on_hotkey_translate_selection)
        self.hotkey_bridge.ocr_translate.connect(self._on_hotkey_ocr_translate)
        self.hotkey_bridge.toggle_float.connect(self._on_hotkey_toggle_float)

    def _setup_tray_menu(self):
        """Add history and settings actions to system tray menu."""
        tray_menu = self.main_window.tray_menu

        # Insert before quit action
        tray_menu.insertSeparator(self.main_window.quit_action)

        history_action = QAction("历史记录", self.main_window)
        history_action.triggered.connect(self._show_history)
        tray_menu.insertAction(self.main_window.quit_action, history_action)

        settings_action = QAction("设置", self.main_window)
        settings_action.triggered.connect(self._show_settings)
        tray_menu.insertAction(self.main_window.quit_action, settings_action)

        float_action = QAction("悬浮窗", self.main_window)
        float_action.triggered.connect(self._on_hotkey_toggle_float)
        tray_menu.insertAction(self.main_window.quit_action, float_action)

        tray_menu.insertSeparator(self.main_window.quit_action)

    def _register_hotkeys(self):
        """Register global hotkeys."""
        hotkeys = self.config.hotkeys
        try:
            self.hotkey_manager.register(
                hotkeys.get('translate_selection', '<ctrl>+<alt>+t'),
                lambda: self.hotkey_bridge.translate_selection.emit()
            )
            self.hotkey_manager.register(
                hotkeys.get('ocr_translate', '<ctrl>+<alt>+o'),
                lambda: self.hotkey_bridge.ocr_translate.emit()
            )
            self.hotkey_manager.register(
                hotkeys.get('show_float_window', '<ctrl>+<alt>+f'),
                lambda: self.hotkey_bridge.toggle_float.emit()
            )
        except Exception as e:
            print(f"Warning: Failed to register hotkeys: {e}")

    def _on_translate(self, text: str, source_lang: str, target_lang: str):
        """Handle translation from main window."""
        self._do_translate(text, source_lang, target_lang, self._on_main_result)

    def _on_float_translate(self, text: str, source_lang: str, target_lang: str):
        """Handle translation from float window."""
        self._do_translate(text, source_lang, target_lang, self._on_popup_result)

    def _do_translate(self, text: str, source_lang: str, target_lang: str, callback):
        """Perform translation asynchronously."""
        priority = self.config.translation.get('priority', ['google'])
        worker = TranslationWorker(
            self.translators, priority, text, source_lang, target_lang
        )
        worker.finished.connect(callback)
        worker.error.connect(self._on_translate_error)
        self._workers.append(worker)

        thread = threading.Thread(target=worker.run, daemon=True)
        thread.start()

    def _on_main_result(self, result: TranslationResult, engine_name: str):
        """Show result in main window and save to history."""
        self.main_window.set_translation_result(result)
        self._save_history(result, engine_name)
        self._cleanup_workers()

    def _on_popup_result(self, result: TranslationResult, engine_name: str):
        """Show result in popup and save to history."""
        self.result_popup.show_result(
            result.original_text, result.text, lang=result.target_lang
        )
        self._save_history(result, engine_name)
        self._cleanup_workers()

    def _on_translate_error(self, msg: str):
        """Handle translation error."""
        print(f"Translation error: {msg}")
        self._cleanup_workers()

    def _save_history(self, result: TranslationResult, engine_name: str):
        """Save translation result to history."""
        try:
            self.history.add_record(
                result.original_text,
                result.text,
                result.source_lang,
                result.target_lang,
                engine_name
            )
        except Exception as e:
            print(f"Failed to save history: {e}")

    def _cleanup_workers(self):
        """Remove finished workers."""
        self._workers = [w for w in self._workers if w is not None]

    # --- Hotkey handlers ---

    def _on_hotkey_translate_selection(self):
        """Translate currently selected text."""
        text = ClipboardManager.get_selection()
        if not text.strip():
            text = ClipboardManager.get_text()
        if text.strip():
            self._do_translate(text.strip(), 'auto', 'zh', self._on_popup_result)

    def _on_hotkey_ocr_translate(self):
        """Screenshot -> OCR -> translate."""
        image_path = ScreenshotManager.capture_region()
        if image_path:
            try:
                if self.ocr.is_available():
                    ocr_result = self.ocr.recognize(image_path, lang='auto')
                    if ocr_result.text.strip():
                        self._do_translate(
                            ocr_result.text.strip(), 'auto', 'zh',
                            self._on_popup_result
                        )
            except Exception as e:
                print(f"OCR failed: {e}")
            finally:
                try:
                    os.unlink(image_path)
                except OSError:
                    pass

    def _on_hotkey_toggle_float(self):
        """Toggle float window visibility."""
        if self.float_window.isVisible():
            self.float_window.hide()
        else:
            from PyQt6.QtGui import QCursor
            self.float_window.show_at(QCursor.pos())

    # --- TTS handlers ---

    def _on_speak_source(self):
        """Speak source text from main window."""
        text = self.main_window.input_text.toPlainText().strip()
        if text:
            self._on_speak(text, 'en')

    def _on_speak_translated(self):
        """Speak translated text from main window."""
        text = self.main_window.output_text.toPlainText().strip()
        if text:
            self._on_speak(text, 'zh')

    def _on_speak(self, text: str, lang: str):
        """Play TTS in background thread."""
        if self.tts and self.tts.is_available():
            thread = threading.Thread(
                target=self._play_tts, args=(text, lang), daemon=True
            )
            thread.start()

    def _play_tts(self, text: str, lang: str):
        """TTS playback (runs in thread)."""
        try:
            self.tts.play_text(text, lang)
        except Exception as e:
            print(f"TTS error: {e}")

    # --- Dialog handlers ---

    def _show_history(self):
        """Show history dialog."""
        dialog = HistoryDialog(self.history, self.main_window)
        dialog.record_selected.connect(
            lambda text: self.main_window.input_text.setPlainText(text)
        )
        dialog.exec()

    def _show_settings(self):
        """Show settings dialog and reload config on accept."""
        dialog = SettingsDialog(self.config_manager, self.main_window)
        if dialog.exec():
            self._reload_config()

    def _reload_config(self):
        """Reload config and reinitialize services."""
        self.config = self.config_manager.load()
        self.hotkey_manager.stop()
        self.translators.clear()
        self._init_translators()
        self._init_tts()
        self._register_hotkeys()

    # --- Lifecycle ---

    def _signal_handler(self, signum, frame):
        self.quit()

    def run(self):
        self.main_window.show()
        self.main_window.tray_icon.show()

        # Show float window on startup if configured
        if self.config.ui.get('float_window_visible', False):
            self.float_window.show()

        return self.app.exec()

    def quit(self):
        self.hotkey_manager.stop()
        self.app.quit()


def main():
    app = TranslatorApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
