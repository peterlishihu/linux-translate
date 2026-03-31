import pytest
from unittest.mock import patch, MagicMock
from src.core.translation.youdao import YoudaoTranslator


class TestYoudaoTranslator:
    def test_is_available_with_config(self):
        translator = YoudaoTranslator(appkey="test", appsecret="test")
        assert translator.is_available() is True

    def test_is_available_without_config(self):
        translator = YoudaoTranslator()
        assert translator.is_available() is False

    def test_translate_mock(self):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "errorCode": "0",
                "query": "hello",
                "translation": ["你好"],
                "basic": {"phonetic": "həˈləʊ"}
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            translator = YoudaoTranslator(appkey="test", appsecret="test")
            result = translator.translate("hello", "en", "zh")
            assert result.text == "你好"
