import time
from type.ASCII import ASCII

#IMPORTANT: CHECK BELOW FOR NOTES AND INFORMATION @Hardware


try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("[WARN] RPi.GPIO not available - simulation mode")
    
#-------------------------------------------------------------------------------------------   
#PIN MAPPING - change here when working on hardware
#format: 'char': GPIO_Pin_Number (BCM)  <-- TODO: !!!

CHAR_TO_PIN: dict[str, int] = {
    ' ':  2,   # Space
    '.':  3,   # Period
    ':':  4,   # Colon
    '=':  17,  # Equal
    '+':  27,  # Plus
    '*':  22,  # Asterisk
    '#':  10,  # Hashtag
    '%':  9,   # Percent
    '@':  11,  # At
    '\n': 14,  # Carriage Return / Line Feed  <- TODO: pins from board here, currently random setup
}

#-------------------------------------------------------------------------------------------  
#Timing - in seconds, TODO: change according to typewriter speed

PULSE_DURATION = 0.05       #how long is signal on high in relais (cur: 50ms)
CHAR_DELAY = 0.1            #pause between chars (cur: 100ms)
CR_DELAY = 0.3              #pause after carriage return (cur: 300ms)


class RpiTypeWriter():
    #currently simulation mode - only logging
    #cur model: Raspberry Pi Zero 2W
    #uses GPIO (BCM) for relais control
    
    def __init__(
        self,
        char_map: dict[str, int] = CHAR_TO_PIN,
        pulse_duration: float = PULSE_DURATION,
        char_delay: float = CHAR_DELAY,
        cr_delay: float = CR_DELAY,
    ) -> None:
        self._char_map      = char_map
        self._pulse         = pulse_duration
        self._char_delay    = char_delay
        self._cr_delay      = cr_delay
        self._simulation    = not GPIO_AVAILABLE
        
    def setup(self) -> None:
        """sets alls mapped pins as outputs and pulls them low"""
        if self._simulation:
            print("[SIM] setup() — all pins initialized")
            return
        GPIO.setmode(GPIO.BCM)
        for pin in self._char_map.values():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        print("[GPIO] setup() done")
        
    def print_ascii(self, ascii: ASCII) -> None:
        """prints the grid"""
        for row in ascii.grid:
            for char in row:
                self.print_char(char)
            self.carriage_return()
            
    def print_char(self, char: str) -> None:
        """maps char to pin"""
        if char not in self._char_map:
            print(f"[WARN] char '{char}' not mapped - skipped")
            return
        
        pin = self._char_map[char]
        
        if self._simulation:
            print(f"[SIM] print_char('{char}') -> pin {pin} HIGH for {self._pulse}s")
        else:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(self._pulse)
            GPIO.output(pin, GPIO.LOW)
        
        time.sleep(self._char_delay)
        
    def carriage_return(self) -> None:
        """carriage return — uses '\n' pin from mapping"""
        if '\n' not in self._char_map:
            print("[WARN] cr-pin undefined - skipped")
            return

        pin = self._char_map['\n']

        if self._simulation:
            print(f"[SIM] carriage_return() -> pin {pin} HIGH for {self._pulse}s")
        else:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(self._pulse)
            GPIO.output(pin, GPIO.LOW)

        time.sleep(self._cr_delay)
        
    def cleanup(self) -> None:
        """sets all pins on LOW - is always executed"""
        if self._simulation:
            print("[SIM] cleanup() — all pins on LOW")
            return
        GPIO.cleanup()
        print("[GPIO] cleanup() done")
        
        
    #------------------------------------------------------------------------------------------- 
    #NOTES FOR HARDWARE
    
    #USING THIS:
    
    """
    from implementation.RpiTypewriterDriver import RpiTypewriterDriver

    driver = RpiTypewriterDriver()
        try:
            driver.setup()
            driver.print_ascii(ascii_art)
    finally:
        driver.cleanup()   # must always execute
    """
    
    #TODO's:
    
    # 1)  CHAR_TO_PIN needs to be set up once wiring is set. BCM numbering refers to the GPIO numbers, not the physical pin numbers on the board
    # 2)  Simulation-Mode: as long as RPi.GPIO is not installed (on the machine), the code runs in a simulation mode producing only log outputs. Pipeline can be tested without the Pi in Simulation Mode
    # 3)  Timing - PULSE_DURATION and CHAR_DELAY need to be empirically determined on the typewriter: too short will result in relais not triggering, too lang will result in long waiting times for printing
    # 4) if the typewriter also has Line Feed, add a second key ('\r') to the mapping and extend carriage_return() to trigger a second pulse
    
    #-----
    
    #Further information:
    
    #currently code does Active-High (GPIO.HIGH = Relais on). if relais are active-low, change HIGH and LOW in code
    
    