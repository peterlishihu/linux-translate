# src/main.py
import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.gui.main_window import MainWindow
from src.config import ConfigManager
from src.db.history import HistoryManager
from src.core.translation import GoogleTranslator, BaiduTranslator


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

        # Create main window
        self.main_window = MainWindow()
        self.main_window.translate_requested.connect(self._on_translate)

        # Setup signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)

    def _init_translators(self):
        # Google Translator
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

    def _on_translate(self, text: str, source_lang: str, target_lang: str):
        # Try translators in priority order
        priority = self.config.translation.get('priority', ['google'])
        for engine_name in priority:
            if engine_name in self.translators:
                try:
                    result = self.translators[engine_name].translate(
                        text, source_lang, target_lang
                    )
                    self.main_window.set_translation_result(result)
                    # Save to history
                    self.history.add_record(
                        result.original_text,
                        result.text,
                        result.source_lang,
                        result.target_lang,
                        engine_name
                    )
                    return
                except Exception as e:
                    print(f"Translation failed with {engine_name}: {e}")
                    continue

        self.main_window.set_translation_result(None)

    def _signal_handler(self, signum, frame):
        self.quit()

    def run(self):
        self.main_window.show()
        return self.app.exec()

    def quit(self):
        self.app.quit()


def main():
    app = TranslatorApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
