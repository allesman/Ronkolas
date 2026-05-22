from abc import ABC, abstractmethod
from pathlib import Path
from type.Image import Image
from type.ASCII import ASCII

class ASCIIConverter(ABC):
    @abstractmethod
    def convert(self, img: Image) -> ASCII:
        ...

    @abstractmethod
    def set_charset(self, charset: str) -> None:
        ...

    @abstractmethod
    def pixel_to_char(self, value: int) -> str:
        ...