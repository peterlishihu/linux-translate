import pytest
from unittest.mock import patch, MagicMock
from src.core.ocr.base import OCRResult
from src.core.ocr.tesseract import TesseractOCR


class TestOCRResult:
    def test_result_creation(self):
        result = OCRResult(text="hello", confidence=95.5)
        assert result.text == "hello"
        assert result.confidence == 95.5


class TestTesseractOCR:
    def test_is_available_with_tesseract(self):
        with patch('shutil.which', return_value='/usr/bin/tesseract'):
            ocr = TesseractOCR()
            assert ocr.is_available() is True

    def test_is_available_without_tesseract(self):
        with patch('shutil.which', return_value=None):
            ocr = TesseractOCR()
            assert ocr.is_available() is False

    def test_recognize_mock(self):
        with patch('shutil.which', return_value='/usr/bin/tesseract'), \
             patch('pytesseract.image_to_string', return_value="hello world"), \
             patch('pytesseract.image_to_data', return_value={
                 'conf': [-1, 95, 90],
                 'text': ['', 'hello', 'world']
             }), \
             patch('PIL.Image.open') as mock_open:

            mock_image = MagicMock()
            mock_open.return_value = mock_image

            ocr = TesseractOCR()
            result = ocr.recognize("/path/to/image.png", lang='eng')
            assert result.text == "hello world"
