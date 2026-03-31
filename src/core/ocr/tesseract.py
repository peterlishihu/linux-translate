import shutil
import pytesseract
from PIL import Image
from .base import OCREngine, OCRResult


class TesseractOCR(OCREngine):
    def __init__(self):
        self._tesseract_cmd = None

    @property
    def name(self) -> str:
        return "tesseract"

    def is_available(self) -> bool:
        cmd = shutil.which('tesseract')
        if cmd:
            self._tesseract_cmd = cmd
            pytesseract.pytesseract.tesseract_cmd = cmd
            return True
        return False

    def recognize(self, image_path: str, lang: str = 'eng') -> OCRResult:
        if not self.is_available():
            raise OCRError("Tesseract is not available")

        try:
            # Map language codes
            lang_map = {'zh': 'chi_sim+chi_tra', 'en': 'eng', 'auto': 'chi_sim+eng'}
            tesseract_lang = lang_map.get(lang, lang)

            # Open image
            image = Image.open(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(image, lang=tesseract_lang)

            # Get confidence data
            try:
                data = pytesseract.image_to_data(image, lang=tesseract_lang, output_type=pytesseract.Output.DICT)
                confidences = [int(c) for c in data['conf'] if int(c) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else None
            except:
                avg_confidence = None

            return OCRResult(text=text.strip(), confidence=avg_confidence)

        except Exception as e:
            raise OCRError(f"OCR recognition failed: {e}")


class OCRError(Exception):
    pass
