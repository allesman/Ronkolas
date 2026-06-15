import copy
from abc import ABC, abstractmethod

import numpy as np

from type.Image import Image

CHAR_ASPECT_RATIO = 0.523

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

    # def floyd_steinberg(self, img: Image, contrast: float = 3.0) -> Image:
    #     pixels = np.array(img.pixels, dtype=np.float32).reshape((img.height, img.width))
    #     # S-curve: push midtones toward black/white before dithering
    #     pixels = pixels / 255.0
    #     pixels = 1.0 / (1.0 + np.exp(-contrast * (pixels - 0.5) * 8))
    #     pixels = np.clip(pixels * 255.0, 0, 255)
    #     for y in range(img.height):
    #         for x in range(img.width):
    #             old = pixels[y, x]
    #             new = 255.0 if old >= 128 else 0.0
    #             pixels[y, x] = new
    #             err = old - new
    #             if x + 1 < img.width:
    #                 pixels[y, x+1]       += err * 7/16
    #             if y + 1 < img.height:
    #                 if x > 0:
    #                     pixels[y+1, x-1] += err * 3/16
    #                 pixels[y+1, x]       += err * 5/16
    #                 if x + 1 < img.width:
    #                     pixels[y+1, x+1] += err * 1/16
    #     return Image(width=img.width, height=img.height,
    #                  pixels=np.clip(pixels, 0, 255).astype(np.uint8),
    #                  mode="GRAY", source_path=img.source_path)

    def sobel(self, img: Image) -> Image:
        p = np.pad(np.array(img.pixels, dtype=np.float32).reshape((img.height, img.width)),
                   1, mode='edge')
        gx = (-p[:-2,:-2] + p[:-2,2:] - 2*p[1:-1,:-2] + 2*p[1:-1,2:] - p[2:,:-2] + p[2:,2:])
        gy = (-p[:-2,:-2] - 2*p[:-2,1:-1] - p[:-2,2:] + p[2:,:-2] + 2*p[2:,1:-1] + p[2:,2:])
        mag = np.sqrt(gx**2 + gy**2)
        if mag.max() > 0:
            mag = mag / mag.max() * 255
        # blend edges onto original: preserves tonal range, boosts structure
        original = np.array(img.pixels, dtype=np.float32).reshape((img.height, img.width))
        blended = original + 1.5 * mag
        mn, mx = blended.min(), blended.max()
        if mx > mn:
            blended = (blended - mn) / (mx - mn) * 255
        return Image(width=img.width, height=img.height,
                     pixels=np.clip(blended, 0, 255).astype(np.uint8),
                     mode="GRAY", source_path=img.source_path)

    def kuwahara(self, img: Image, radius: int = 2) -> Image:
        pixels = np.array(img.pixels, dtype=np.float32).reshape((img.height, img.width))
        r = radius
        s = r + 1
        p = np.pad(pixels, r, mode='edge')
        h, w = img.height, img.width
        wins = np.lib.stride_tricks.sliding_window_view(p, (s, s))  # (h+r, w+r, s, s)
        means = np.empty((4, h, w), dtype=np.float32)
        variances = np.empty((4, h, w), dtype=np.float32)
        for i, (dr, dc) in enumerate([(0,0),(0,r),(r,0),(r,r)]):
            flat = wins[dr:dr+h, dc:dc+w].reshape(h, w, s*s)
            means[i] = flat.mean(axis=-1)
            variances[i] = flat.var(axis=-1)
        best = np.argmin(variances, axis=0)
        result = means[best, np.arange(h)[:,None], np.arange(w)[None,:]]
        return Image(width=img.width, height=img.height,
                     pixels=np.clip(result, 0, 255).astype(np.uint8),
                     mode="GRAY", source_path=img.source_path)

    def _save_preview(self, img: Image, label: str, path: str = "preview.png") -> None:
        from PIL import Image as PilImage
        pixels = np.array(img.pixels, dtype=np.uint8).reshape((img.height, img.width))
        PilImage.fromarray(pixels, mode="L").save(path)

    def custom_alg(self, img: Image, alg: int) -> Image:
        output=img
        if alg == 2:
            output= self.kuwahara(img)
        elif alg == 3:
            output =  self.sobel(img)
        # ts ugly
        # elif alg == 2:
        #     output = self.floyd_steinberg(img)
        self._save_preview(output, f"PREVIEW_{alg}", f"preview_alg{alg}.png")
        return output


    def compress (self, img: Image, char_aspect_ratio: float = CHAR_ASPECT_RATIO) -> Image:
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