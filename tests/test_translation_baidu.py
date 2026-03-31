# tests/test_translation_baidu.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.translation.baidu import BaiduTranslator


class TestBaiduTranslator:
    def test_is_available_with_config(self):
        translator = BaiduTranslator(appid="test", key="test")
        assert translator.is_available() is True

    def test_is_available_without_config(self):
        translator = BaiduTranslator()
        assert translator.is_available() is False

    def test_translate_mock(self):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "from": "en",
                "to": "zh",
                "trans_result": [{"src": "hello", "dst": "你好"}]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            translator = BaiduTranslator(appid="test", key="test")
            result = translator.translate("hello", "en", "zh")
            assert result.text == "你好"
