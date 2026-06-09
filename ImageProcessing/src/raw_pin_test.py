try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    GPIO = None
    print("[WARN] RPi.GPIO not available - cannot test")
    exit(1)

PINS = list(range(0, 10))

GPIO.setmode(GPIO.BCM)
for pin in PINS:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

print(f"Valid GPIO pins: {PINS}")
print("Enter a pin number to pulse LOW for 50ms (q to quit):\n")

try:
    while True:
        raw = input("> ")
        if raw == "q":
            break
        try:
            pin = int(raw)
        except ValueError:
            print(f"[SKIP] '{raw}' is not a number")
            continue
        if pin not in PINS:
            print(f"[SKIP] GPIO {pin} not in list")
            continue
        import time
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.1)
        print(f"[OK] pulsed GPIO {pin}")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up")

