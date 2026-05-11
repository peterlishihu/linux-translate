# src/core/translation/argos.py
from .base import TranslationEngine, TranslationResult


class ArgosTranslator(TranslationEngine):
    """Offline translation engine using argostranslate (English <-> Chinese)"""

    def __init__(self):
        self._models_checked = False

    @property
    def name(self) -> str:
        return "argos"

    def is_available(self) -> bool:
        try:
            import argostranslate.translate
            installed = argostranslate.translate.get_installed_languages()
            lang_codes = [lang.code for lang in installed]
            return 'en' in lang_codes and 'zh' in lang_codes
        except (ImportError, Exception):
            return False

    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'zh') -> TranslationResult:
        if source_lang == 'auto':
            source_lang = self._detect_language(text)

        from_code = self._normalize_lang(source_lang)
        to_code = self._normalize_lang(target_lang)

        if from_code == to_code:
            return TranslationResult(
                text=text,
                source_lang=from_code,
                target_lang=to_code,
                original_text=text
            )

        try:
            import argostranslate.translate
        except ImportError:
            raise RuntimeError("argostranslate is not installed. Run: pip install argostranslate")

        translated = argostranslate.translate.translate(text, from_code, to_code)

        return TranslationResult(
            text=translated,
            source_lang=from_code,
            target_lang=to_code,
            original_text=text
        )

    def ensure_models_installed(self) -> bool:
        """Download and install en<->zh translation models if not present.

        Returns True if models are ready, False on failure.
        Requires internet connection on first run.
        """
        try:
            import argostranslate.package
            import argostranslate.translate

            installed = argostranslate.translate.get_installed_languages()
            lang_codes = [lang.code for lang in installed]
            if 'en' in lang_codes and 'zh' in lang_codes:
                self._models_checked = True
                return True

            argostranslate.package.update_package_index()
            available = argostranslate.package.get_available_packages()

            en_zh = next(
                (p for p in available if p.from_code == 'en' and p.to_code == 'zh'),
                None
            )
            if en_zh:
                argostranslate.package.install_from_path(en_zh.download())

            zh_en = next(
                (p for p in available if p.from_code == 'zh' and p.to_code == 'en'),
                None
            )
            if zh_en:
                argostranslate.package.install_from_path(zh_en.download())

            self._models_checked = True
            return True

        except ImportError:
            return False
        except Exception as e:
            print(f"Failed to install Argos models: {e}")
            return False

    @staticmethod
    def _detect_language(text: str) -> str:
        """Simple heuristic: if >70% ASCII characters, treat as English; else Chinese."""
        if not text:
            return 'en'
        ascii_count = sum(1 for c in text if ord(c) < 128)
        ratio = ascii_count / len(text)
        return 'en' if ratio > 0.7 else 'zh'

    @staticmethod
    def _normalize_lang(lang: str) -> str:
        """Normalize language code to argos format."""
        lang_map = {
            'zh': 'zh',
            'cn': 'zh',
            'chinese': 'zh',
            'en': 'en',
            'english': 'en',
        }
        return lang_map.get(lang.lower(), lang)
