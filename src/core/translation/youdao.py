import requests
import hashlib
import uuid
import time
from .base import TranslationEngine, TranslationResult


class YoudaoTranslator(TranslationEngine):
    BASE_URL = "https://openapi.youdao.com/api"

    def __init__(self, appkey: str = None, appsecret: str = None, timeout: int = 10):
        self.appkey = appkey
        self.appsecret = appsecret
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "youdao"

    def is_available(self) -> bool:
        return bool(self.appkey and self.appsecret)

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        if not self.is_available():
            raise TranslationError("Youdao translator not configured")

        salt = uuid.uuid4().hex
        curtime = str(int(time.time()))
        sign_str = self.appkey + self._truncate(text) + salt + curtime + self.appsecret
        sign = hashlib.sha256(sign_str.encode()).hexdigest()

        # Language code mapping
        lang_map = {'zh': 'zh-CHS', 'en': 'en', 'auto': 'auto'}
        from_lang = lang_map.get(source_lang, source_lang)
        to_lang = lang_map.get(target_lang, target_lang)

        payload = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appKey': self.appkey,
            'salt': salt,
            'sign': sign,
            'signType': 'v3',
            'curtime': curtime
        }

        try:
            response = requests.post(self.BASE_URL, data=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data.get('errorCode') != '0':
                raise TranslationError(f"Youdao API error: {data.get('errorCode')}")

            translated = ' '.join(data.get('translation', []))
            return TranslationResult(
                text=translated,
                source_lang=from_lang,
                target_lang=to_lang,
                original_text=text,
                pronunciation=data.get('basic', {}).get('phonetic')
            )
        except Exception as e:
            raise TranslationError(f"Youdao translate failed: {e}")

    def _truncate(self, text: str) -> str:
        """Truncate text for sign generation (youdao requirement)"""
        if len(text) <= 20:
            return text
        return text[:10] + str(len(text)) + text[-10:]


class TranslationError(Exception):
    pass
