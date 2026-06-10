import time

from type.ASCII import ASCII

# IMPORTANT: CHECK BELOW FOR NOTES AND INFORMATION @Hardware


try:
    import RPi.GPIO as GPIO

    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("[WARN] RPi.GPIO not available - simulation mode. Or something went wrong with GPIO setup. Check if RPi.GPIO is installed and you are running on a Raspberry Pi.")

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
    # currently simulation mode - only logging
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
        self._simulation = not GPIO_AVAILABLE

    def setup(self) -> None:
        """sets all pins used in mapping as outputs and pulls them high"""
        if self._simulation:
            print("[SIM] setup() — all pins initialized")
            return
        GPIO.setmode(GPIO.BCM)
        used_pins = {pin for pins in self._char_map.values() for pin in pins}
        for pin in used_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
        print("[GPIO] setup() done")

    def print_ascii(self, ascii_grid: ASCII) -> None:
        """prints the grid"""
        for row in ascii_grid.grid:
            for char in row:
                self.print_char(char)
            self.carriage_return()

    def _pulse_pins(self, pins: tuple[int, ...]) -> None:
        """pulls pins LOW, waits pulse duration, then pulls HIGH again"""
        if self._simulation:
            print(f"[SIM] pulse pins {pins} LOW for {self._pulse}s")
        else:
            for pin in pins:
                GPIO.output(pin, GPIO.LOW)
            time.sleep(self._pulse)
            for pin in pins:
                GPIO.output(pin, GPIO.HIGH)

    def print_char(self, char: str) -> None:
        """pulses all pins mapped to char simultaneously"""
        print(f"[INFO] print_char('{char}')")
        if char not in self._char_map:
            print(f"[WARN] char '{char}' not mapped - skipped")
            return
        self._pulse_pins(self._char_map[char])
        time.sleep(self._char_delay)

    def carriage_return(self) -> None:
        """carriage return — uses '\\n' pins from mapping"""
        if "\n" not in self._char_map:
            print("[WARN] cr-pin undefined - skipped")
            return
        self._pulse_pins(self._char_map["\n"])
        time.sleep(self._cr_delay)

    def cleanup(self) -> None:
        """releases all GPIO pins (resets to input mode) - is always executed"""
        if self._simulation:
            print("[SIM] cleanup() — all pins released")
            return
        GPIO.cleanup()
        print("[GPIO] cleanup() done")

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
    # - [ ] CHAR_TO_PIN needs to be set up once wiring is set. BCM numbering refers to the GPIO numbers, not the physical pin numbers on the board
    # - [ ] Timing: PULSE_DURATION and CHAR_DELAY need to be empirically determined on the typewriter: too short will result in relais not triggering, too lang will result in long waiting times for printing
    # - [ ] Timing optimization: hold down shift pin for consecutive shifted chars to avoid multiple pulses on shift pin.

    # -----

    # useful info:
    # - Simulation-Mode: as long as RPi.GPIO is not installed (on the machine), the code runs in a simulation mode producing only log outputs. Pipeline can be tested without the Pi in Simulation Mode
    # - if the typewriter also has Line Feed, add a second key ('\r') to the mapping and extend carriage_return() to trigger a second pulse

    # -----

    # Further information:
