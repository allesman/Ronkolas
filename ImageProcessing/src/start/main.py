from pathlib import Path
from interface import ImageLoader
from interface.ImageLoader import BmpImageLoader
from type.Image import Image

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

search_directory = Path("../Images_for_testing/")
image_Loader = BmpImageLoader()

found_image = find_and_load_image(search_directory,image_Loader)
if found_image:
    print(f"found {found_image.source_path}")