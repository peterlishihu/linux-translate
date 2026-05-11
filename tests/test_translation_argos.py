# tests/test_translation_argos.py
import sys
import pytest
from unittest.mock import patch, MagicMock
from src.core.translation.base import TranslationResult
from src.core.translation.argos import ArgosTranslator


# Create mock argostranslate modules for testing
def _setup_argos_mock():
    """Setup mock argostranslate modules."""
    mock_translate_module = MagicMock()
    mock_package_module = MagicMock()
    mock_argos = MagicMock()
    mock_argos.translate = mock_translate_module
    mock_argos.package = mock_package_module
    return mock_argos, mock_translate_module, mock_package_module


class TestArgosTranslator:
    def test_name(self):
        translator = ArgosTranslator()
        assert translator.name == "argos"

    def test_is_available_no_package(self):
        with patch.dict(sys.modules, {
            'argostranslate': None,
            'argostranslate.translate': None
        }):
            translator = ArgosTranslator()
            assert translator.is_available() is False

    def test_is_available_with_models(self):
        mock_argos, mock_translate_mod, _ = _setup_argos_mock()
        mock_lang_en = MagicMock()
        mock_lang_en.code = 'en'
        mock_lang_zh = MagicMock()
        mock_lang_zh.code = 'zh'
        mock_translate_mod.get_installed_languages.return_value = [mock_lang_en, mock_lang_zh]

        with patch.dict(sys.modules, {
            'argostranslate': mock_argos,
            'argostranslate.translate': mock_translate_mod
        }):
            translator = ArgosTranslator()
            assert translator.is_available() is True

    def test_is_available_without_models(self):
        mock_argos, mock_translate_mod, _ = _setup_argos_mock()
        mock_lang_en = MagicMock()
        mock_lang_en.code = 'en'
        mock_translate_mod.get_installed_languages.return_value = [mock_lang_en]

        with patch.dict(sys.modules, {
            'argostranslate': mock_argos,
            'argostranslate.translate': mock_translate_mod
        }):
            translator = ArgosTranslator()
            assert translator.is_available() is False

    def test_translate_en_to_zh(self):
        mock_argos, mock_translate_mod, _ = _setup_argos_mock()
        mock_translate_mod.translate.return_value = "你好世界"

        with patch.dict(sys.modules, {
            'argostranslate': mock_argos,
            'argostranslate.translate': mock_translate_mod
        }):
            translator = ArgosTranslator()
            result = translator.translate("hello world", "en", "zh")
            assert result.text == "你好世界"
            assert result.source_lang == "en"
            assert result.target_lang == "zh"
            assert result.original_text == "hello world"

    def test_translate_zh_to_en(self):
        mock_argos, mock_translate_mod, _ = _setup_argos_mock()
        mock_translate_mod.translate.return_value = "hello world"

        with patch.dict(sys.modules, {
            'argostranslate': mock_argos,
            'argostranslate.translate': mock_translate_mod
        }):
            translator = ArgosTranslator()
            result = translator.translate("你好世界", "zh", "en")
            assert result.text == "hello world"
            assert result.source_lang == "zh"
            assert result.target_lang == "en"

    def test_translate_auto_detect_english(self):
        mock_argos, mock_translate_mod, _ = _setup_argos_mock()
        mock_translate_mod.translate.return_value = "你好"

        with patch.dict(sys.modules, {
            'argostranslate': mock_argos,
            'argostranslate.translate': mock_translate_mod
        }):
            translator = ArgosTranslator()
            result = translator.translate("hello", "auto", "zh")
            assert result.source_lang == "en"
            assert result.target_lang == "zh"

    def test_translate_auto_detect_chinese(self):
        mock_argos, mock_translate_mod, _ = _setup_argos_mock()
        mock_translate_mod.translate.return_value = "hello"

        with patch.dict(sys.modules, {
            'argostranslate': mock_argos,
            'argostranslate.translate': mock_translate_mod
        }):
            translator = ArgosTranslator()
            result = translator.translate("你好世界", "auto", "en")
            assert result.source_lang == "zh"
            assert result.target_lang == "en"

    def test_translate_same_language(self):
        translator = ArgosTranslator()
        result = translator.translate("hello", "en", "en")
        assert result.text == "hello"

    def test_detect_language_english(self):
        assert ArgosTranslator._detect_language("hello world") == "en"
        assert ArgosTranslator._detect_language("This is a test.") == "en"

    def test_detect_language_chinese(self):
        assert ArgosTranslator._detect_language("你好世界") == "zh"
        assert ArgosTranslator._detect_language("这是一个测试") == "zh"

    def test_detect_language_empty(self):
        assert ArgosTranslator._detect_language("") == "en"

    def test_normalize_lang(self):
        assert ArgosTranslator._normalize_lang("zh") == "zh"
        assert ArgosTranslator._normalize_lang("cn") == "zh"
        assert ArgosTranslator._normalize_lang("en") == "en"
        assert ArgosTranslator._normalize_lang("english") == "en"
        assert ArgosTranslator._normalize_lang("chinese") == "zh"

    def test_ensure_models_already_installed(self):
        mock_argos, mock_translate_mod, mock_package_mod = _setup_argos_mock()
        mock_lang_en = MagicMock()
        mock_lang_en.code = 'en'
        mock_lang_zh = MagicMock()
        mock_lang_zh.code = 'zh'
        mock_translate_mod.get_installed_languages.return_value = [mock_lang_en, mock_lang_zh]

        with patch.dict(sys.modules, {
            'argostranslate': mock_argos,
            'argostranslate.translate': mock_translate_mod,
            'argostranslate.package': mock_package_mod
        }):
            translator = ArgosTranslator()
            assert translator.ensure_models_installed() is True
            mock_package_mod.update_package_index.assert_not_called()

    def test_ensure_models_no_package(self):
        with patch.dict(sys.modules, {
            'argostranslate': None,
            'argostranslate.package': None,
            'argostranslate.translate': None
        }):
            translator = ArgosTranslator()
            assert translator.ensure_models_installed() is False
