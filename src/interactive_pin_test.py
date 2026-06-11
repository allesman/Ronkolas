from TypewriterDriver import RpiTypeWriter, CHAR_TO_PIN

# collect all unique pins from mapping
ALL_PINS = sorted({pin for pins in CHAR_TO_PIN.values() for pin in pins})

driver = RpiTypeWriter()
try:
    driver.setup()
    print(f"Valid GPIO pins: {ALL_PINS}")
    print("Enter a pin number to pulse (q to quit):\n")
    while True:
        raw = input("> ")
        if raw == "q":
            break
        try:
            pin = int(raw)
        except ValueError:
            print(f"[SKIP] '{raw}' is not a number")
            continue
        if pin not in ALL_PINS:
            print(f"[SKIP] GPIO {pin} not in mapping")
            continue
        driver._pulse_pins((pin,))
finally:
    driver.cleanup()

