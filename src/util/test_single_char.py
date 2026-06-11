from src.TypewriterDriver import RpiTypeWriter

CHAR = "8"  # change to whichever char you want to test

driver = RpiTypeWriter()
try:
    driver.setup()
    driver.print_char(CHAR)
finally:
    driver.cleanup()
