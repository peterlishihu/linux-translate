# tests/test_translation_google.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.translation.base import TranslationResult
from src.core.translation.google import GoogleTranslator


class TestTranslationResult:
    def test_result_creation(self):
        result = TranslationResult(
            text="你好",
            source_lang="en",
            target_lang="zh",
            original_text="hello"
        )
        assert result.text == "你好"
        assert result.source_lang == "en"


class TestGoogleTranslator:
    def test_is_available(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            translator = GoogleTranslator()
            assert translator.is_available() is True

    def test_translate_mock(self):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [[["hello world", "你好世界", None, None, 1]], None, "en"]
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            translator = GoogleTranslator()
            result = translator.translate("hello world", "en", "zh")
            assert result.text == "你好世界"
            assert result.source_lang == "en"
            assert result.target_lang == "zh"
