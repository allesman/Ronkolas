import copy
from abc import ABC, abstractmethod
from pathlib import Path
from type.Image import Image
import numpy as np

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

    @abstractmethod
    def compress (self, img: Image, char_aspect_ratio: float) -> Image:
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
        pixels_np = np.array(gray_pixels, dtype=np.uint8).reshape((img.height, img.width))
        return Image(
            width=img.width,
            height=img.height,
            pixels=pixels_np,
            mode="GRAY",
            source_path=img.source_path
        )
    def normalize(self, img: Image) -> Image:
        pixels = np.array(img.pixels, dtype=np.float32)
        flat = pixels.flatten()

        min_val = flat.min()
        max_val = flat.max()

        if max_val == min_val:
            return copy.deepcopy(img)
        
        normalized = ((pixels - min_val) / (max_val - min_val) * 255)
        normalized = np.clip(normalized, 0, 255).astype(np.uint8)

        return Image(
            width=img.width,
            height=img.height,
            pixels=normalized,
            mode=img.mode,
            source_path=img.source_path
        )
    def adjust_contrast(self, img: Image, factor: float) -> Image:
        pixels = np.array(img.pixels, dtype=np.float32)
        adjusted = 128 + factor * (pixels - 128)
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return Image(
            width=img.width,
            height=img.height,
            pixels=adjusted,
            mode=img.mode,
            source_path=img.source_path
        )
    def compress (self, img: Image, char_aspect_ratio: float = 0.5) -> Image:
        pixels = np.array(img.pixels, dtype = np.float32)
        if pixels.ndim == 1:
            channels = 1 if img.mode == "GRAY" else 3
            pixels = pixels.reshape ((img.height, img.width, channels)) if channels > 1 \
                else pixels.reshape((img.height, img.width))
        new_height = max(1, int(img.height * char_aspect_ratio))
        row_indices = np.round(np.linspace(0, img.height - 1, new_height)).astype(int)
        compressed = pixels[row_indices]
        compressed = np.clip(compressed, 0, 255).astype(np.uint8)

        return Image (
            width = img.width,
            height = new_height,
            pixels = compressed,
            mode = img.mode,
            source_path = img.source_path,
        )