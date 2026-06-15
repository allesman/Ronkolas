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

# IMPORTANT: THIS NEEDS TO BE DISABLED BEFORE PUSHING!
DEBUG_MODE = False

STD_PATH = Path("/home/pi/Ronkolas/assets/advisor-logo.bmp")
USB_Path = Path("/media/pi")       #unsure was hier der richtige Path ist, nachschauen auf raspi, wie der usb stick abspeichert? evtl /media/pi TODO:

if DEBUG_MODE:
    # override paths
    STD_PATH = Path("MOCK_USB/mountain.bmp")
    USB_Path = Path("MOCK_USB")

#potentially needs adjustment in img loading as unsure how usb stick works
CONTRAST_FAC = 1.0
MODE_STANDARD = 0
MODE_ALG1 = 1
MODE_ALG2 = 2
MODE_ALG3 = 3

class Orchestrator:
    def __init__(self, contrast_factor: float, source: str, alg: int = 0) -> None:
        self._loader = BmpImageLoader()
        self._preProc = ImagePreprocessor()
        self._converter = RampAsciiConverter(mode=alg)
        self._driver = RpiTypeWriter()
        self._log = StdLogger()
        self._contrast = contrast_factor
        self._alg = alg
        self._src = source # can either be usb for usb stick or file for local file
        
    def run(self,callback) -> bool:
        try:
            img_path = None
            if self._src == "usb":
                img_path = self._find_image_on_usb()
            else:
                img_path = self._get_file_path()
            if img_path is None:
                self._log.error("no img found on usb - stopped")
                return False
            img = self._load(img_path)
            ascii = self._process_and_convert(img)
            if DEBUG_MODE:
                self._debug_print_to_file(ascii)
                self._log.info("DEBUG MODE: printed ascii to file instead of typewriter")
                return True
            self._print(ascii, callback)
            self._log.info("pipeline fully executed")
            return True
        except Exception as e:
            self._log.error("there was an error while executing pipeline", e)
            return False
        
    def _get_file_path(self) -> Path:
        return STD_PATH
    
    def _find_image_on_usb(self) -> Path | None:
        self._log.info(f"Search for USB in {USB_Path}")
        if not USB_Path.exists():
            self._log.warn(f"no such path: {USB_Path}")
            return None
        for path in USB_Path.rglob("*.bmp"):
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

        custom_alg_applied = self._preProc.custom_alg(contrasted,self._alg)

        squeezed = self._preProc.compress(custom_alg_applied)

        self._log.info("preprocessing done")

        # custom alg id is also passed here, since inversion is applied in this step and not custom_alg()
        ascii_grid = self._converter.convert(squeezed, self._alg)

        self._log.info("conversion done")
        return ascii_grid
    
    def _debug_print_to_file(self, ascii_grid: ASCII, path: str = "debug_output.txt") -> None:
        with open(path, "w") as f:
            for row in ascii_grid.grid:
                f.write("".join(row) + "\n")
        self._log.info(f"debug output written to {path}")

    def _print(self, ascii_grid: ASCII, callback) -> None:
        self._log.info("start printing")
        self._driver.setup()
        try:
            a = self._driver.print_ascii(ascii_grid, callback)
            # Paper feed: holds CR to pull artwork into display frame via weights.
            # Fixed duration for now — TODO: replace with button/sensor input once hardware is ready.
            PAPER_FEED_DURATION = 10.0  # seconds — adjust to what works with frame distance & size
            if a:
                self._driver.feed_paper(PAPER_FEED_DURATION)
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
    
    orchestrator = Orchestrator(contrast_factor=CONTRAST_FAC, source="usb", alg=MODE_STANDARD)
    success = orchestrator.run(callback=lambda: logging.info("Callback: Print job completed."))
    
    if not success:
        exit(1)
