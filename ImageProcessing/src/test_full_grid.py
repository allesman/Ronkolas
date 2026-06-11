from TypewriterDriver import RpiTypeWriter,CHAR_TO_PIN
from type.ASCII import ASCII

# 64x64 grid using only all mapped chars (except \n) for testing
CHARS = sorted(CHAR_TO_PIN.keys())
if '\n' in CHARS:
    CHARS.remove('\n')

SIZE = 64
grid = [
    [CHARS[(row * SIZE + col) % len(CHARS)] for col in range(SIZE)]
    for row in range(SIZE)
]

ascii_art = ASCII(grid=grid, width=SIZE, height=SIZE, charset="")

driver = RpiTypeWriter()
try:
    driver.setup()
    driver.print_ascii(ascii_art)
finally:
    driver.cleanup()

