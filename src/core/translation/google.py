import requests
import json
from .base import TranslationEngine, TranslationResult


class GoogleTranslator(TranslationEngine):
    BASE_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "google"

    def is_available(self) -> bool:
        try:
            response = requests.get(
                self.BASE_URL,
                params={'client': 'gtx', 'sl': 'auto', 'tl': 'en', 'dt': 't', 'q': 'test'},
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception:
            return False

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        params = {
            'client': 'gtx',
            'sl': source_lang if source_lang != 'auto' else 'auto',
            'tl': target_lang,
            'dt': 't',
            'q': text
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            translated = ''.join(item[0] for item in data[0] if item[0])
            detected_lang = data[2] if len(data) > 2 and data[2] else source_lang

            return TranslationResult(
                text=translated,
                source_lang=detected_lang,
                target_lang=target_lang,
                original_text=text
            )
        except Exception as e:
            raise TranslationError(f"Google translate failed: {e}")


class TranslationError(Exception):
    pass
