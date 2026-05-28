import copy
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
class ImagePreprocessor(Preprocessor):
    def to_grayscale(self, img: Image) -> Image:
        if img.mode == "GRAY":
            return copy.deepcopy(img)
        gray_pixels = []
        for i in range(0,len(img.pixels),3):
            r = img.pixels[i]
            g = img.pixels[i+1]
            b = img.pixels[i+2]
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            gray_pixels.append(gray)
        return Image(
            width=img.width,
            height=img.height,
            pixels=gray_pixels,
            mode="GRAY",
            source_path=img.source_path
        )
    def normalize(self, img: Image) -> Image:
        if not img.pixels:
            return copy.deepcopy(img)

        min_val = min(img.pixels)
        max_val = max(img.pixels)
        if max_val == min_val:
            return copy.deepcopy(img)
        norm_pixels = [
            int(((p - min_val) / (max_val - min_val)) * 255)
            for p in img.pixels
        ]

        return Image(
            width=img.width,
            height=img.height,
            pixels=norm_pixels,
            mode=img.mode,
            source_path=img.source_path
        )
    def adjust_contrast(self, img: Image, factor: float) -> Image:
        new_pixels = []

        for p in img.pixels:
            new_val = int(128 + factor * (p - 128))
            new_val = max(0, min(255, new_val))

            new_pixels.append(new_val)

        return Image(
            width=img.width,
            height=img.height,
            pixels=new_pixels,
            mode=img.mode,
            source_path=img.source_path
        )