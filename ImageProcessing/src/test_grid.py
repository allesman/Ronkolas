from TypewriterDriver import RpiTypeWriter
from type.ASCII import ASCII

# 64x64 grid using only non-shifted chars for testing
UNSHIFTED_CHARS = [' ', ',', '8', '4', '3', '2', '=', 'l']

SIZE = 64
grid = [
    [UNSHIFTED_CHARS[(row * SIZE + col) % len(UNSHIFTED_CHARS)] for col in range(SIZE)]
    for row in range(SIZE)
]

ascii_art = ASCII(grid=grid, width=SIZE, height=SIZE, charset="")

driver = RpiTypeWriter()
try:
    driver.setup()
    driver.print_ascii(ascii_art)
finally:
    driver.cleanup()

