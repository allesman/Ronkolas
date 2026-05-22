from abc import ABC, abstractmethod
from pathlib import Path
from type.Image import Image

class Preprocessor(ABC):
    @abstractmethod
    def to_grayscale(self, img: Image) -> Image:
        ...

    @abstractmethod
    def normalize(self, img: Image) -> Image:
        ...

    @abstractmethod
    def adjust_contrast(self, img: Image, factor: float) -> Image:
        ...