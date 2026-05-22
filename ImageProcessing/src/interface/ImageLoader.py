from abc import ABC, abstractmethod
from pathlib import Path
from type.Image import Image

class ImageLoader(ABC):
    @abstractmethod
    def load(self, path: Path) -> Image:
        ...

    @abstractmethod
    def is_supported(self, path: Path) -> bool:
        ...

    @abstractmethod
    def validate(self, img: Image) -> bool:
        ...

