from abc import ABC, abstractmethod


class TTSEngine(ABC):
    @abstractmethod
    def play_text(self, text: str, lang: str = 'zh') -> bool:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class TTSError(Exception):
    pass
