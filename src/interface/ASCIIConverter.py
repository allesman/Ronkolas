from abc import ABC, abstractmethod
from pathlib import Path
from type.Image import Image
from type.ASCII import ASCII
import numpy as np

class ASCIIConverter(ABC):
    @abstractmethod
    def convert(self, img: Image) -> ASCII:
        ...

    @abstractmethod
    def set_charset(self, charset: str) -> None:
        ...

    @abstractmethod
    def pixel_to_char(self, value: int) -> str:
        ...

#Implementation

#notes for charsets (experiences):
    #heavier weight on sparse characters makes image more appealing
    #fastest printwise: space biased charsets with stretched characters produce repetitive patterns with more spaces in the result
    #nearly optimal: "   ....====+*#8$#@" -> combines small space bias with repetitive char patterns, but still some variation to avoid clusters

MAX_CHARSET = " ,+=*lL2438$#@" # max chars

REALISTIC_MAX_CHARSET = " .=+*#8$@" # remove opacity duplicates

REALISTIC_MAX_CHARSET_BIASED = "   ....====+*#8$@" # biased towards less opacity

REDUCED_CHARSET = " .=+*#%@" # less chars, faster printing

FAST_CHARSET = "   .=+*#@" # bias towards space for even faster printing

MORE_FAST_CHARSET = "        ...=+*#@" # bias towards space for even faster printing

# IMPORTANT: might get overridden in constructor, depending on mode (this is only used for modes 2 and 3 rn)
STANDARD_CHARSET = REDUCED_CHARSET     #ADJUST CHARSET HERE


class RampAsciiConverter(ASCIIConverter):
    """
    grayscale pixel values to ASCII-characters via brightness ramp
    """

    def __init__(self, charset: str = STANDARD_CHARSET, mode:int = 0) -> None:
        """
        Args:
            charset:    brightness ramp, must have >= 2 chars
                        Convention: index 0 brightest, last index = darkest. e.g. " .:=+*#%@"
        """
        # TODO?
        if mode == 1: #inversion alg/filter/mode
            self.set_charset(charset[::-1]) #reverse charset for inverted ramp
        if mode==0: # standard mode, no alg/filter applied
            self.set_charset(REALISTIC_MAX_CHARSET_BIASED)
        else: # other modes (could also add clause for mode 2 or 3, 0 stays default)
            self.set_charset(charset)

    def set_charset(self, charset: str) -> None:
        """
        replace active char ramo, with valueBound handling

        Args:
            charset:    same as init
        """
        if len(charset) < 2:
            raise ValueError("charset should have at least 2 chars, got {len(charset)}")
        self._charset = charset

    def pixel_to_char(self, value) -> str:
        """
        maps single grayscale value (0,255) to single char -> using linear interpolation across len
        ---
        0 (black) -> densest character (last in charset, e.g. @)
        255 (white) -> sparsest character (first in charset, e.g. ' ')
        ---
        -> returns single ASCII char from active charset

        Args:
            value:      grayscale intensity (has to be in (0,255))
        """
        value = int(value) #cast: uint8 -> int, for potentail overflow when *
        if not (0 <= value <= 255):
            raise ValueError("pixel value not in 0-255, got {value}")
        
        n = len(self._charset)
        idx = (n - 1) - int(value * (n - 1) / 255)

        return self._charset[idx]
    
    def convert(self, image: Image, algorithm: int) -> ASCII:
        """
        converts grayscale img to ASCII grid
        -> returns  ASCII, with grid[row][col] = one char per pixel

        Args:
            image:      Grayscale Image, from output of preprocessor
        """
        if image.mode != "GRAY":
            raise ValueError("not in grayscale, got mode: '{image.mode}'")
        
        vectorized = np.vectorize(self.pixel_to_char)
        char_array = vectorized(image.pixels)

        grid = [list(row) for row in char_array]

        return ASCII(
            grid=grid,
            width=image.width,
            height=image.height,
            charset=self._charset,
        )