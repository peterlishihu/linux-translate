import threading
from .base import TTSEngine, TTSError


class OfflineTTS(TTSEngine):
    def __init__(self, rate: int = 150):
        self.rate = rate
        self._engine = None

    @property
    def name(self) -> str:
        return "offline"

    def is_available(self) -> bool:
        try:
            import pyttsx3
            return True
        except ImportError:
            return False

    def _get_engine(self):
        if self._engine is None:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self.rate)
        return self._engine

    def play_text(self, text: str, lang: str = 'zh') -> bool:
        if not text or not text.strip():
            return False

        try:
            engine = self._get_engine()

            # Set voice based on language
            voices = engine.getProperty('voices')
            if lang == 'zh':
                # Try to find Chinese voice
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            else:
                # Default to English
                for voice in voices:
                    if 'english' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break

            engine.say(text)
            engine.runAndWait()
            return True

        except Exception as e:
            raise TTSError(f"Offline TTS failed: {e}")

    def stop(self):
        """Stop current speech"""
        if self._engine:
            try:
                self._engine.stop()
            except:
                pass
