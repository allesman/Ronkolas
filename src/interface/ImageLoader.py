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



class BmpImageLoader(ImageLoader):
    def is_supported(self, path: Path) -> bool:
        return path.suffix.lower() == ".bmp"

    def validate(self, img: Image) -> bool:
        return img.width == 64 and img.height == 64

    def load(self, path: Path) -> Image:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not self.is_supported(path):
            raise ValueError(f"{path} not supported")

        with path.open("rb") as f:
            header = f.read(54)

            if len(header) < 54 or header[0:2] != b"BM":
                raise ValueError("File format not valid")

            width = int.from_bytes(header[18:22], byteorder="little", signed=True)
            height_raw = int.from_bytes(header[22:26], byteorder="little", signed=True)
            bits = int.from_bytes(header[28:30], byteorder="little")
            pixel_offset = int.from_bytes(header[10:14], byteorder="little")

            is_top_down = height_raw < 0
            height = abs(height_raw)

            print(f"[DEBUG] Lade BMP: {width}x{height}, Bits pro Pixel: {bits}")

            if bits not in [24, 32]:
                raise ValueError(f"Nicht unterstützte Farbtiefe: {bits}-Bit. Bitte 24-Bit oder 32-Bit nutzen.")

            f.seek(pixel_offset)

            bytes_per_pixel = bits // 8

            row_stride = ((bits * width + 31) // 32) * 4
            padding_size = row_stride - (width * bytes_per_pixel)

            rows = []
            for _ in range(height):
                row_data = list(f.read(width * bytes_per_pixel))
                f.read(padding_size)

                rgb_row = []
                for i in range(0, len(row_data), bytes_per_pixel):
                    b = row_data[i]
                    g = row_data[i + 1]
                    r = row_data[i + 2]
                    rgb_row.extend([r, g, b])

                rows.append(rgb_row)

            pixel_data = []
            for row in (rows if is_top_down else reversed(rows)):
                pixel_data.extend(row)

            img = Image(
                width=width,
                height=height,
                pixels=pixel_data,
                mode="RGB",
                source_path=str(path),
            )

            if not self.validate(img):
                print(f"[WARNUNG] Bild {path.name} ist nicht 64x64 Pixel groß (ist {width}x{height}).")

            return img