from PIL import Image as PILImage

from pathlib import Path
from interface import ImageLoader
from interface.ImageLoader import BmpImageLoader
from interface.Preprocessor import ImagePreprocessor
from interface.ASCIIConverter import RampAsciiConverter
from type.Image import Image
import os
import numpy as np

def find_and_load_image(directory:Path,loader:ImageLoader) -> Image|None:
    for path in directory.glob("*.bmp"):
        if loader.is_supported(path):
            try:
                image = loader.load(path)
                if loader.validate(image):
                    print(f"Image found")
                    return image
                else:
                    print(f"try next one")
            except Exception as e:
                print(f"Error: {e}")
    return None



#Testing
def show_image(custom_img: Image):
    """Konvertiert dein Image-Objekt in ein Pillow-Bild und zeigt es an."""
    pixels = custom_img.pixels
    if isinstance(pixels, np.ndarray):
        pixels = pixels.flatten()

    # 1. Sicherstellen, dass alle Werte zwischen 0 und 255 liegen (wichtig für bytes)
    clamped_pixels = [max(0, min(255, int(p))) for p in pixels]
    pixel_bytes = bytes(clamped_pixels)

    pil_mode = "RGB" if custom_img.mode == "RGB" else "L"

    # 2. Fehleranalyse: Prüfen ob die Byte-Menge zur Auflösung passt
    expected_bytes = custom_img.width * custom_img.height * (3 if pil_mode == "RGB" else 1)
    if len(pixel_bytes) != expected_bytes:
        print(f"[FEHLER in show_image] Byte-Anzahl stimmt nicht!")
        print(f"-> Erwartet: {expected_bytes} Bytes ({custom_img.width}x{custom_img.height})")
        print(f"-> Bekommen: {len(pixel_bytes)} Bytes")
        return

    try:
        # Bild aus den Bytes erstellen
        pil_img = PILImage.frombytes(pil_mode, (custom_img.width, custom_img.height), pixel_bytes)

        # Öffnet das Bild im Standard-Bildbetrachter
        pil_img.show()
    except Exception as e:
        print(f"[FEHLER] Pillow konnte das Bild nicht rendern: {e}")

def show_ascii(ascii_art):
    print("\n--- ASCII preview ---")
    for row in ascii_art.grid:
        print("".join(row))
    print("---\n")
    output_path = Path(os.getcwd()) / "output_ascii.txt"
    with output_path.open("w", encoding="utf-8") as f:
        for row in ascii_art.grid:
            f.write("".join(row) + "\n")
    print(f"[output] written to {output_path.resolve()}")


search_directory = Path("../Images_for_testing/")
image_Loader = BmpImageLoader()

found_image = find_and_load_image(search_directory,image_Loader)
if found_image:
    print(f"found {found_image.source_path}")
    print("opening image viewer...")

    show_image(found_image)
    pre = ImagePreprocessor()
    gray = pre.to_grayscale(found_image)
    normalized = pre.normalize(gray)
    high_contrast = pre.adjust_contrast(normalized,1.5)

    show_image(high_contrast)

    #ascii
    converter = RampAsciiConverter()
    ascii = converter.convert(high_contrast)
    print(f"[ascii] grid {ascii.height}x{ascii.width}, charset='{ascii.charset}'")
    show_ascii(ascii)




