from TypewriterDriver import RpiTypeWriter

UNSHIFTED = {' ', ',', '8', '4', '3', '2', '=', ';'}

driver = RpiTypeWriter()
try:
    driver.setup()
    print(f"Valid chars: {' '.join(sorted(UNSHIFTED))}")
    print("Type a char and press Enter (q to quit):\n")
    while True:
        raw = input("> ")
        if raw == "q":
            break
        if len(raw) != 1 or raw not in UNSHIFTED:
            print(f"[SKIP] '{raw}' not a valid unshifted char")
            continue
        driver.print_char(raw)
finally:
    driver.cleanup()

