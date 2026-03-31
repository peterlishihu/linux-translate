from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranslationResult:
    text: str
    source_lang: str
    target_lang: str
    original_text: str
    pronunciation: Optional[str] = None


class TranslationEngine(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
