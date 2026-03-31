# src/core/translation/baidu.py
import requests
import hashlib
import random
from .base import TranslationEngine, TranslationResult


class BaiduTranslator(TranslationEngine):
    BASE_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def __init__(self, appid: str = None, key: str = None, timeout: int = 10):
        self.appid = appid
        self.key = key
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "baidu"

    def is_available(self) -> bool:
        return bool(self.appid and self.key)

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        if not self.is_available():
            raise TranslationError("Baidu translator not configured")

        salt = random.randint(32768, 65536)
        sign_str = self.appid + text + str(salt) + self.key
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        # Language code mapping
        lang_map = {'zh': 'zh', 'en': 'en', 'auto': 'auto'}
        from_lang = lang_map.get(source_lang, source_lang)
        to_lang = lang_map.get(target_lang, target_lang)

        payload = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }

        try:
            response = requests.post(self.BASE_URL, data=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if 'error_code' in data:
                raise TranslationError(f"Baidu API error: {data['error_msg']}")

            translated = ''.join(item['dst'] for item in data['trans_result'])
            return TranslationResult(
                text=translated,
                source_lang=data.get('from', source_lang),
                target_lang=data.get('to', target_lang),
                original_text=text
            )
        except Exception as e:
            raise TranslationError(f"Baidu translate failed: {e}")


class TranslationError(Exception):
    pass
