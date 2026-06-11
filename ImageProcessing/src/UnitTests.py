import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))

from type.Image import Image
from type.ASCII import ASCII
from interface.Preprocessor import ImagePreprocessor
from interface.ASCIIConverter import RampAsciiConverter
from interface.ImageLoader import BmpImageLoader
from TypewriterDriver import RpiTypeWriter, SHIFT_PIN, CR_DELAY, POST_SHIFT_DELAY

TEST_BMP_3x3 = Path(__file__).parent / "Images_for_testing" / "test_3x3.bmp"

# -------------------------------------------------------------------------------------------
# Helpers

def make_rgb_image(pixels_rgb_flat: list[int], width: int, height: int) -> Image:
    return Image(width=width, height=height, pixels=pixels_rgb_flat, mode="RGB", source_path="test")

def make_gray_image(pixels_flat, width: int, height: int) -> Image:
    arr = np.array(pixels_flat, dtype=np.uint8).reshape((height, width))
    return Image(width=width, height=height, pixels=arr, mode="GRAY", source_path="test")

# 3x3 RGB image: top-left black, top-right white, rest mid-gray
#   R   G   B
BLACK = [0,   0,   0  ]
WHITE = [255, 255, 255]
GRAY  = [128, 128, 128]

RGB_3x3 = (
    BLACK + GRAY  + WHITE +   # row 0
    GRAY  + GRAY  + GRAY  +   # row 1
    WHITE + GRAY  + BLACK     # row 2
)


# -------------------------------------------------------------------------------------------
# Preprocessor: to_grayscale

class TestToGrayscale:
    def setup_method(self):
        self.proc = ImagePreprocessor()

    def test_output_mode_is_gray(self):
        img = make_rgb_image(RGB_3x3, 3, 3)
        result = self.proc.to_grayscale(img)
        assert result.mode == "GRAY"

    def test_output_dimensions_preserved(self):
        img = make_rgb_image(RGB_3x3, 3, 3)
        result = self.proc.to_grayscale(img)
        assert result.width == 3 and result.height == 3

    def test_pure_black_maps_to_0(self):
        img = make_rgb_image(BLACK * 9, 3, 3)
        result = self.proc.to_grayscale(img)
        assert result.pixels.flatten().tolist() == [0] * 9

    def test_pure_white_maps_to_255(self):
        img = make_rgb_image(WHITE * 9, 3, 3)
        result = self.proc.to_grayscale(img)
        assert result.pixels.flatten().tolist() == [255] * 9

    def test_already_gray_returns_copy(self):
        img = make_gray_image([100] * 9, 3, 3)
        result = self.proc.to_grayscale(img)
        assert result is not img
        assert result.pixels.flatten().tolist() == [100] * 9

    def test_luma_formula(self):
        # single pixel R=100 G=150 B=200 -> 0.299*100 + 0.587*150 + 0.114*200 = 140.65 -> 140
        img = make_rgb_image([100, 150, 200], 1, 1)
        result = self.proc.to_grayscale(img)
        assert result.pixels.flatten()[0] == int(0.299 * 100 + 0.587 * 150 + 0.114 * 200)


# -------------------------------------------------------------------------------------------
# Preprocessor: normalize

class TestNormalize:
    def setup_method(self):
        self.proc = ImagePreprocessor()

    def test_min_becomes_0_max_becomes_255(self):
        img = make_gray_image([50, 100, 150, 200, 250, 100, 50, 200, 150], 3, 3)
        result = self.proc.normalize(img)
        flat = result.pixels.flatten().tolist()
        assert min(flat) == 0
        assert max(flat) == 255

    def test_uniform_image_unchanged(self):
        img = make_gray_image([128] * 9, 3, 3)
        result = self.proc.normalize(img)
        assert result.pixels.flatten().tolist() == [128] * 9

    def test_output_dimensions_preserved(self):
        img = make_gray_image(list(range(9)), 3, 3)
        result = self.proc.normalize(img)
        assert result.width == 3 and result.height == 3

    def test_mode_preserved(self):
        img = make_gray_image(list(range(9)), 3, 3)
        result = self.proc.normalize(img)
        assert result.mode == "GRAY"


# -------------------------------------------------------------------------------------------
# Preprocessor: adjust_contrast

class TestAdjustContrast:
    def setup_method(self):
        self.proc = ImagePreprocessor()

    def test_factor_1_unchanged(self):
        pixels = [0, 64, 128, 192, 255, 100, 50, 200, 10]
        img = make_gray_image(pixels, 3, 3)
        result = self.proc.adjust_contrast(img, 1.0)
        assert result.pixels.flatten().tolist() == pixels

    def test_factor_0_all_128(self):
        img = make_gray_image([0, 64, 128, 192, 255, 100, 50, 200, 10], 3, 3)
        result = self.proc.adjust_contrast(img, 0.0)
        assert all(v == 128 for v in result.pixels.flatten().tolist())

    def test_high_contrast_clamps_to_0_255(self):
        img = make_gray_image([0, 255] + [128] * 7, 3, 3)
        result = self.proc.adjust_contrast(img, 10.0)
        flat = result.pixels.flatten().tolist()
        assert all(0 <= v <= 255 for v in flat)

    def test_output_dimensions_preserved(self):
        img = make_gray_image([128] * 9, 3, 3)
        result = self.proc.adjust_contrast(img, 1.5)
        assert result.width == 3 and result.height == 3


# -------------------------------------------------------------------------------------------
# ASCIIConverter: pixel_to_char

class TestPixelToChar:
    def setup_method(self):
        self.conv = RampAsciiConverter(" .:#@")  # 5-char ramp

    def test_white_255_maps_to_first_char(self):
        assert self.conv.pixel_to_char(255) == " "

    def test_black_0_maps_to_last_char(self):
        assert self.conv.pixel_to_char(0) == "@"

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            self.conv.pixel_to_char(256)
        with pytest.raises(ValueError):
            self.conv.pixel_to_char(-1)

    def test_charset_too_short_raises(self):
        with pytest.raises(ValueError):
            RampAsciiConverter("x")


# -------------------------------------------------------------------------------------------
# ASCIIConverter: convert

class TestConvert:
    def setup_method(self):
        self.conv = RampAsciiConverter()

    def test_output_grid_dimensions(self):
        img = make_gray_image(list(range(9)), 3, 3)
        result = self.conv.convert(img)
        assert result.height == 3
        assert result.width == 3
        assert len(result.grid) == 3
        assert all(len(row) == 3 for row in result.grid)

    def test_rejects_non_gray_image(self):
        img = make_rgb_image(RGB_3x3, 3, 3)
        with pytest.raises(ValueError):
            self.conv.convert(img)

    def test_all_white_produces_all_space(self):
        img = make_gray_image([255] * 9, 3, 3)
        result = self.conv.convert(img)
        assert all(c == " " for row in result.grid for c in row)

    def test_all_black_produces_all_dense(self):
        img = make_gray_image([0] * 9, 3, 3)
        result = self.conv.convert(img)
        last_char = self.conv._charset[-1]
        assert all(c == last_char for row in result.grid for c in row)

    def test_grid_contains_only_charset_chars(self):
        img = make_gray_image(list(range(0, 255, 28))[:9], 3, 3)
        result = self.conv.convert(img)
        for row in result.grid:
            for c in row:
                assert c in self.conv._charset


# -------------------------------------------------------------------------------------------
# Full pipeline integration (no I/O, no driver)

class TestFullPipeline:
    def test_rgb_to_ascii_grid_shape(self):
        proc = ImagePreprocessor()
        conv = RampAsciiConverter()

        img = make_rgb_image(RGB_3x3, 3, 3)
        gray = proc.to_grayscale(img)
        normalized = proc.normalize(gray)
        contrasted = proc.adjust_contrast(normalized, 1.0)
        ascii_grid = conv.convert(contrasted)

        assert ascii_grid.width == 3
        assert ascii_grid.height == 3
        assert len(ascii_grid.grid) == 3

    def test_uniform_white_image_gives_all_spaces(self):
        proc = ImagePreprocessor()
        conv = RampAsciiConverter()

        img = make_rgb_image(WHITE * 9, 3, 3)
        ascii_grid = conv.convert(proc.normalize(proc.to_grayscale(img)))

        assert all(c == " " for row in ascii_grid.grid for c in row)


# -------------------------------------------------------------------------------------------
# BmpImageLoader

class TestBmpImageLoader:
    def setup_method(self):
        self.loader = BmpImageLoader()

    def test_is_supported_bmp(self):
        assert self.loader.is_supported(Path("image.bmp")) is True
        assert self.loader.is_supported(Path("image.BMP")) is True

    def test_is_supported_rejects_other_extensions(self):
        assert self.loader.is_supported(Path("image.png")) is False
        assert self.loader.is_supported(Path("image.jpg")) is False

    def test_validate_passes_for_64x64(self):
        img = Image(width=64, height=64, pixels=[], mode="RGB", source_path="")
        assert self.loader.validate(img) is True

    def test_validate_fails_for_wrong_size(self):
        assert self.loader.validate(Image(width=3, height=3, pixels=[], mode="RGB", source_path="")) is False
        assert self.loader.validate(Image(width=64, height=32, pixels=[], mode="RGB", source_path="")) is False

    def test_load_returns_image_with_correct_dimensions(self):
        img = self.loader.load(TEST_BMP_3x3)
        assert img.width == 3
        assert img.height == 3

    def test_load_returns_rgb_mode(self):
        img = self.loader.load(TEST_BMP_3x3)
        assert img.mode == "RGB"

    def test_load_pixel_count(self):
        img = self.loader.load(TEST_BMP_3x3)
        # 3x3 RGB = 27 values
        assert len(img.pixels) == 27

    def test_load_raises_for_missing_file(self):
        with pytest.raises(FileNotFoundError):
            self.loader.load(Path("nonexistent.bmp"))

    def test_load_raises_for_unsupported_extension(self):
        # loader checks extension before reading, but file must exist — use any existing non-bmp
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            with pytest.raises(ValueError):
                self.loader.load(Path(f.name))


# -------------------------------------------------------------------------------------------
# TypewriterDriver

def make_driver() -> RpiTypeWriter:
    """Create a driver with zero delays for fast tests."""
    return RpiTypeWriter(pulse_duration=0, char_delay=0, cr_delay=0)

def make_ascii(chars: list[list[str]]) -> ASCII:
    return ASCII(grid=chars, width=len(chars[0]), height=len(chars), charset=" @")


class TestPrintChar:
    def setup_method(self):
        self.driver = make_driver()

    def test_unmapped_char_is_skipped(self):
        with patch.object(self.driver, '_pulse_pin') as mock_pulse:
            self.driver.print_char('?')
            mock_pulse.assert_not_called()

    def test_unshifted_char_pulses_correct_pin(self):
        with patch.object(self.driver, '_pulse_pin') as mock_pulse, \
             patch.object(self.driver, '_set_shift') as mock_shift:
            self.driver.print_char(' ')
            mock_pulse.assert_called_once_with(11)
            mock_shift.assert_not_called()

    def test_shifted_char_sets_shift_then_pulses_char_pin(self):
        with patch.object(self.driver, '_pulse_pin') as mock_pulse, \
             patch.object(self.driver, '_set_shift') as mock_shift:
            self.driver.print_char('*')  # maps to (SHIFT_PIN, 2)
            mock_shift.assert_any_call(True)
            mock_pulse.assert_called_once_with(2)

    def test_shifted_char_releases_shift_when_shift_after_false(self):
        with patch.object(self.driver, '_pulse_pin'), \
             patch.object(self.driver, '_set_shift') as mock_shift:
            self.driver.print_char('*', shift_after=False)
            assert call(False) in mock_shift.call_args_list

    def test_shifted_char_keeps_shift_when_shift_after_true(self):
        with patch.object(self.driver, '_pulse_pin'), \
             patch.object(self.driver, '_set_shift') as mock_shift:
            self.driver.print_char('*', shift_after=True)
            assert call(False) not in mock_shift.call_args_list

    def test_shift_pin_is_not_pulsed_directly(self):
        with patch.object(self.driver, '_pulse_pin') as mock_pulse, \
             patch.object(self.driver, '_set_shift'):
            self.driver.print_char('#')  # (SHIFT_PIN, 4)
            pulsed_pins = [c.args[0] for c in mock_pulse.call_args_list]
            assert SHIFT_PIN not in pulsed_pins


class TestCarriageReturn:
    def test_uses_cr_delay(self):
        driver = make_driver()
        with patch.object(driver, 'print_char') as mock_print:
            driver.carriage_return()
            mock_print.assert_called_once_with('\n', shift_after=False, delay=CR_DELAY)

    def test_skipped_when_newline_not_mapped(self):
        driver = RpiTypeWriter(char_map={' ': (11,)}, pulse_duration=0, char_delay=0, cr_delay=0)
        with patch.object(driver, 'print_char') as mock_print:
            driver.carriage_return()
            mock_print.assert_not_called()


class TestPrintAscii:
    def test_each_char_printed_once(self):
        driver = make_driver()
        grid = make_ascii([['*', ' '], ['@', ',']])
        printed = []
        with patch.object(driver, 'print_char', side_effect=lambda c, *a, **kw: printed.append(c)), \
             patch.object(driver, 'carriage_return'):
            driver.print_ascii(grid)
        assert printed == ['*', ' ', '@', ',']

    def test_carriage_return_called_after_each_row(self):
        driver = make_driver()
        grid = make_ascii([[' ', ' '], [' ', ' ']])
        with patch.object(driver, 'print_char'), \
             patch.object(driver, 'carriage_return') as mock_cr:
            driver.print_ascii(grid)
        assert mock_cr.call_count == 2

    def test_shift_after_true_when_next_char_is_shifted(self):
        driver = make_driver()
        # row: [' ', '*'] — next of ' ' is '*' (shifted), so shift_after should be True
        grid = make_ascii([[' ', '*']])
        calls = []
        with patch.object(driver, 'print_char', side_effect=lambda c, shift_after=False, **kw: calls.append((c, shift_after))), \
             patch.object(driver, 'carriage_return'):
            driver.print_ascii(grid)
        assert calls[0] == (' ', True)   # space before shifted char
        assert calls[1] == ('*', False)  # last in row, no lookahead


# -------------------------------------------------------------------------------------------
# Full pipeline integration via Orchestrator

class TestOrchestratorPipeline:
    def _make_orchestrator(self):
        from Orchestrator import Orchestrator
        return Orchestrator(contrast_factor=1.0)

    def test_run_returns_true_with_valid_bmp(self):
        orch = self._make_orchestrator()
        with patch.object(orch, '_find_image_on_usb', return_value=TEST_BMP_3x3), \
             patch.object(orch, '_print'):
            result = orch.run()
        assert result is True

    def test_run_returns_false_when_no_image_found(self):
        orch = self._make_orchestrator()
        with patch.object(orch, '_find_image_on_usb', return_value=None):
            result = orch.run()
        assert result is False

    def test_run_returns_false_on_exception(self):
        orch = self._make_orchestrator()
        with patch.object(orch, '_find_image_on_usb', side_effect=RuntimeError("boom")):
            result = orch.run()
        assert result is False

    def test_ascii_grid_dimensions_match_image(self):
        orch = self._make_orchestrator()
        captured = {}
        with patch.object(orch, '_find_image_on_usb', return_value=TEST_BMP_3x3), \
             patch.object(orch, '_print', side_effect=lambda grid: captured.update({'grid': grid})):
            orch.run()
        assert captured['grid'].width == 3
        assert captured['grid'].height == 3

