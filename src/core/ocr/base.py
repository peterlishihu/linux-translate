from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class OCRResult:
    text: str
    confidence: Optional[float] = None


class OCREngine(ABC):
    @abstractmethod
    def recognize(self, image_path: str, lang: str = 'eng') -> OCRResult:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
