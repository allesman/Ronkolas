import time

from type.ASCII import ASCII

# IMPORTANT: CHECK BELOW FOR NOTES AND INFORMATION @Hardware


try:
    import RPi.GPIO as GPIO

    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("[WARN] If you're testing on a non Raspberry Pi, everything is ok, simulation mode active. Otherwise something went wrong with GPIO setup. Check if RPi.GPIO is installed.")

# -------------------------------------------------------------------------------------------
# PIN MAPPING - change here when working on hardware
# each char maps to a tuple of GPIO pins (BCM) to pulse simultaneously

SHIFT_PIN = 9

CHAR_TO_PIN: dict[str, tuple[int, ...]] = {
    # unshifted
    ' ':  (11,),
    ',':  (10,),
    '8':  (2,),
    '4':  (3,),
    '3':  (4,),
    '2':  (17,),
    '=':  (14,),
    'l':  (8,), # should be semicolon but we messed up the wiring apparently
    # ';':  (8,),
    '\n': (15,),
    # shifted
    '*':  (SHIFT_PIN,2),
    '$':  (SHIFT_PIN, 3),
    '#':  (SHIFT_PIN, 4),
    '@':  (SHIFT_PIN, 17),
    '+':  (SHIFT_PIN, 14),
    'L': (SHIFT_PIN, 8), # should be semicolon but we messed up the wiring apparently
    # ':':  (SHIFT_PIN, 8),
}

# -------------------------------------------------------------------------------------------
# Timing - in seconds, TODO: change according to typewriter speed

PULSE_DURATION = 0.05  # how long is signal on high in relais (cur: 50ms)
CHAR_DELAY = 0.1  # pause between chars (cur: 100ms)
CR_DELAY = 0.3  # pause after carriage return (cur: 300ms)
POST_SHIFT_DELAY = 0.05  # additional pause after shift is pressed



class RpiTypeWriter:
    # logs always; only drives GPIO pins when real hardware is connected
    # cur model: Raspberry Pi Zero 2W
    # uses GPIO (BCM) for relais control

    def __init__(
            self,
            char_map: dict[str, tuple[int, ...]] = CHAR_TO_PIN,
            pulse_duration: float = PULSE_DURATION,
            char_delay: float = CHAR_DELAY,
            cr_delay: float = CR_DELAY,
    ) -> None:
        self._char_map = char_map
        self._pulse = pulse_duration
        self._char_delay = char_delay
        self._cr_delay = cr_delay
        self._real_hardware_connected = GPIO_AVAILABLE

    def setup(self) -> None:
        """sets all pins used in mapping as outputs and pulls them high"""
        if self._real_hardware_connected:
            GPIO.setmode(GPIO.BCM)
            used_pins = {pin for pins in self._char_map.values() for pin in pins}
            for pin in used_pins:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
        print("[GPIO] setup() done")

    def print_ascii(self, ascii_grid: ASCII) -> None:
        print("============")
        """prints the grid"""
        for row in ascii_grid.grid:
            for i in range(len(row)):
                char = row[i]
                if i == len(row) - 1:
                    # last char in row, no lookahead possible, just print without shift optimization
                    self.print_char(char, shift_after=False)
                else:
                    # lookahead to check if next char is shifted for timing optimization
                    next_char = row[i+1]
                    shift_after = self._is_char_shifted(next_char)
                    self.print_char(char,shift_after)
                print("------------")
            self.carriage_return() # can be replaced with print_char('\n') prolly
            print("=============")

    def _pulse_pin(self, pin: int) -> None:
        """pulls pin LOW, waits pulse duration, then pulls HIGH again"""
        print(f"[GPIO] pulse pin {pin} LOW for {self._pulse}s")
        if self._real_hardware_connected:
            GPIO.output(pin, GPIO.LOW)
            time.sleep(self._pulse)
            GPIO.output(pin, GPIO.HIGH)

    def _set_shift(self, pressed: bool) -> None:
        """explicitly set shift pin state"""
        print(f"[GPIO] shift {'DOWN' if pressed else 'UP'}")
        if self._real_hardware_connected:
            GPIO.output(SHIFT_PIN, GPIO.LOW if pressed else GPIO.HIGH)

    def _is_char_shifted(self, char: str) -> bool:
        """returns whether char is shifted (i.e. requires shift key) according to mapping"""
        if char not in self._char_map:
            print(f"[WARN] char '{self.readable_name(char)}' not mapped - cannot determine if shifted")
            return False
        return SHIFT_PIN in self._char_map[char]

    def print_char(self, char: str, shift_after: bool = False, delay: float = None) -> None:
        """
        Prints the supplied char.
        :param char: The char to print. Must be in mapping, otherwise it is skipped with a warning.
        :param shift_after: Whether to keep shift pressed afterward (optimization for consecutive shifted chars)
        :param delay: Optional delay after printing char. If not supplied, default char delay is used.
        """
        if delay is None:
            # the python way to define a default value that is not set at function definition time
            delay = self._char_delay
        print(f"[INFO] will print '{self.readable_name(char)}' now")
        if char not in self._char_map:
            print(f"[WARN] char '{char}' not mapped - skipped")
            return

        pins: tuple[int, ...] = self._char_map[char]
        is_shifted = SHIFT_PIN in pins

        if is_shifted:
            self._set_shift(True)
            time.sleep(POST_SHIFT_DELAY)

        # pulse the actual character pin (skip shift pin)
        for pin in pins:
            if pin != SHIFT_PIN:
                self._pulse_pin(pin)

        if is_shifted and not shift_after:
            self._set_shift(False)

        time.sleep(delay)

    def carriage_return(self) -> None:
        """carriage return — uses '\\n' pins from mapping"""
        if "\n" not in self._char_map:
            print("[WARN] cr-pin undefined - skipped")
            return
        self.print_char("\n", shift_after=False, delay=CR_DELAY)

    def cleanup(self) -> None:
        """releases all GPIO pins (resets to input mode) - is always executed"""
        if self._real_hardware_connected:
            GPIO.cleanup()
        print("[GPIO] cleanup() done")

    @staticmethod
    def readable_name(char) -> str:
        """returns a human-readable name for a char for logging purposes"""
        if char == ' ':
            return "SPACE"
        elif char == '\n':
            return "CR"
        else:
            return char

    # -------------------------------------------------------------------------------------------
    # NOTES FOR HARDWARE

    # USING THIS:

    """
    from implementation.RpiTypewriterDriver import RpiTypewriterDriver

    driver = RpiTypewriterDriver()
        try:
            driver.setup()
            driver.print_ascii(ascii_art)
    finally:
        driver.cleanup()   # must always execute
    """

    # TODO's:

    # - [x] currently code does Active-High (GPIO.HIGH = Relais on). if relais are active-low, change HIGH and LOW in code. note: that is in fact the case, so i changed it
    # - [x] CHAR_TO_PIN needs to be set up once wiring is set. BCM numbering refers to the GPIO numbers, not the physical pin numbers on the board
    # - [/] Timing: PULSE_DURATION and CHAR_DELAY need to be empirically determined on the typewriter: too short will result in relais not triggering, too lang will result in long waiting times for printing
    # - [x] Timing optimization: hold down shift pin for consecutive shifted chars to avoid multiple pulses on shift pin.

    # -----

    # useful info:
    # - Dry-Run Mode: as long as RPi.GPIO is not installed (on the machine), the code runs without driving any pins, producing only log outputs. Pipeline can be tested without the Pi in this mode.
    # - if the typewriter also has Line Feed, add a second key ('\r') to the mapping and extend carriage_return() to trigger a second pulse

    # -----

    # Further information:
