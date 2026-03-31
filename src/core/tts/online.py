import os
import tempfile
from .base import TTSEngine, TTSError


class OnlineTTS(TTSEngine):
    def __init__(self, speed: float = 1.0):
        self.speed = speed

    @property
    def name(self) -> str:
        return "online"

    def is_available(self) -> bool:
        try:
            import gtts
            import pydub
            return True
        except ImportError:
            return False

    def play_text(self, text: str, lang: str = 'zh') -> bool:
        if not text or not text.strip():
            return False

        lang_map = {
            'zh': 'zh-CN',
            'en': 'en',
            'auto': 'zh-CN'
        }
        tts_lang = lang_map.get(lang, lang)

        try:
            from gtts import gTTS
            from pydub import AudioSegment
            from pydub.playback import play

            tts = gTTS(text=text, lang=tts_lang, slow=False)

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp_path = tmp.name

            tts.save(tmp_path)

            # Play audio
            audio = AudioSegment.from_mp3(tmp_path)
            if self.speed != 1.0:
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * self.speed)
                })

            play(audio)
            os.unlink(tmp_path)
            return True

        except Exception as e:
            raise TTSError(f"Online TTS failed: {e}")
