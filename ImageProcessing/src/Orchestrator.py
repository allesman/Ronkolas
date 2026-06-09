import os
import time
from pathlib import Path

from interface.ImageLoader import BmpImageLoader
from interface.Preprocessor import ImagePreprocessor
from interface.ASCIIConverter import RampAsciiConverter
from interface.Logger import StdLogger
from TypewriterDriver import RpiTypeWriter
from type.Image import Image
from type.ASCII import ASCII

USB_Path = Path("/media/pi")       #unsure was hier der richtige Path ist, nachschauen auf raspi, wie der usb stick abspeichert? evtl /media/pi TODO:
#potentially needs adjustment in img loading as unsure how usb stick works
CONTRAST_FAC = 1.0

class Orchestrator:
    def __init__(self, contrast_factor: float) -> None:
        self._loader = BmpImageLoader()
        self._preProc = ImagePreprocessor()
        self._converter = RampAsciiConverter()
        self._driver = RpiTypeWriter()
        self._log = StdLogger()
        self._contrast = contrast_factor
        
    def run(self) -> bool:
        try:
            img_path = self._find_image_on_usb()
            if img_path is None:
                self._log.error("no img found on usb - stopped")
                return False
            img = self._load(img_path)
            ascii = self._process_and_convert(img)
            self._print(ascii)
            self._log.info("pipeline fully executed")
            return True
        except Exception as e:
            self._log.error("there was an error while executing pipeline", e)
            return False
    
    def _find_image_on_usb(self) -> Path | None:
        self._log.info(f"Search for USB in {USB_Path}")
        if not USB_Path.exists():
            self._log.warn(f"no such path: {USB_Path}")
            return None
        for device_dir in USB_Path.iterdir():
            if not device_dir.is_dir():
                continue
            self._log.info(f"searching in {device_dir}")
            for path in device_dir.rglob("*.bmp"):
                if self._loader.is_supported(path):
                    self._log.info(f"bmp found: {path}")
                    return path
        self._log.warn("no bmp found on USB")
        return None
    
    def _load(self, path: Path) -> Image:
        self._log.info(f"loading img: {path.name}")
        img = self._loader.load(path)
        self._log.info(f"loaded image")
        return img
    
    def _process_and_convert(self, image: Image) -> ASCII:
        self._log.info("start image processing")
        gray = self._preProc.to_grayscale(image)
        normalized = self._preProc.normalize(gray)
        contrasted = self._preProc.adjust_contrast(normalized, self._contrast)
        self._log.info("preprocessing done")
        ascii = self._converter.convert(contrasted)
        self._log.info("conversion done")
        return ascii
    
    def _print(self, ascii: ASCII) -> None:
        self._log.info("start printing")
        self._driver.setup()
        try:
            self._driver.print_ascii(ascii)
            try:
                while True:
                    self._driver.carriage_return()
            except KeyboardInterrupt:
                self._log.info("paper feed stopped")

        finally:
            self._driver.cleanup()
        self._log.info("finished printing")
    
    # -----------------------------------
    # entry / main
if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    orchestrator = Orchestrator(contrast_factor = CONTRAST_FAC)
    success = orchestrator.run()
    
    if not success:
        exit(1)
