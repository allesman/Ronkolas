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

    def load(self,path:Path):
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not self.is_supported(path):
            raise ValueError(f"{path} not supported")
        with path.open("rb") as f:
            bmp_file_header = f.read(54)

            if len(bmp_file_header) < 54 or bmp_file_header[0:2] != b"BM":
                raise ValueError("File format not valid")

            width = int.from_bytes(bmp_file_header[18:22],byteorder= "little")
            height = int.from_bytes(bmp_file_header[22:26],byteorder = "little")

            bits = int.from_bytes(bmp_file_header[28:30], byteorder="little")
            mode = "RGB"
            if bits <= 8:
                mode = "GRAY"
            pixel = int.from_bytes(bmp_file_header[10:14],byteorder="little")
            f.seek(pixel)

            pixel_data = list(f.read())
            return Image(
                width = width,
                height = height,
                pixels = pixel_data,
                mode = mode,
                source_path= str(path),
            )