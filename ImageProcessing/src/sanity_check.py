from TypewriterDriver import RpiTypeWriter
from type.ASCII import ASCII

# 3x4 grid using only unshifted (non-modifier) chars
grid = [
    [' ', '8', '4', '3', ';', '2', '=', ' ', ',', '3', '8', ';'],
]

ascii_art = ASCII(grid=grid, width=4, height=3, charset="")

driver = RpiTypeWriter()
try:
    driver.setup()
    driver.print_ascii(ascii_art)
finally:
    driver.cleanup()
