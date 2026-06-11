import time
from Orchestrator import Orchestrator, CONTRAST_FAC

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False

START_PIN = 6 # button: start
SWITCH_MODE = 13 # switch: usb vs. file
# 00 -> Alg1, 01 -> Alg2, 10 -> Alg3, 11 -> Alg4
SWITCH1_PIN = 12
SWITCH2_PIN = 16
LED_R_PIN = 0 # button: LED red = standard mode
LED_G_PIN = 5 # button: LED green = artistic mode


def get_mode() -> str:
    return "file" if GPIO.input(SWITCH_MODE) == GPIO.LOW else "usb"

def get_alg() -> int:
    if GPIO.input(SWITCH1_PIN) == GPIO.LOW and GPIO.input(SWITCH2_PIN) == GPIO.LOW:
        return 0
    elif GPIO.input(SWITCH1_PIN) == GPIO.LOW and GPIO.input(SWITCH2_PIN) == GPIO.HIGH:
        return 1
    elif GPIO.input(SWITCH1_PIN) == GPIO.HIGH and GPIO.input(SWITCH2_PIN) == GPIO.LOW:
        return 2
    elif GPIO.input(SWITCH1_PIN) == GPIO.HIGH and GPIO.input(SWITCH2_PIN) == GPIO.HIGH:
        return 3
    return -1

def set_led(red: bool, green: bool) -> None:
    GPIO.output(LED_R_PIN, GPIO.HIGH if red else GPIO.LOW)
    GPIO.output(LED_G_PIN, GPIO.HIGH if green else GPIO.LOW)

def main():
    #for local testing
    if not GPIO_AVAILABLE:
        print("[WARN] simulation - press enter to start")
        mode = "file"
        while True:
            user_input = input()
            if user_input.strip() in ("file", "usb"):
                mode = user_input.strip()
                print(f"[SIM] set mode to: {mode}")
            else:
                print(f"[SIM] button pressed - starting orchestrator in mode: {mode}")
                Orchestrator(contrast_factor=CONTRAST_FAC, source=mode).run()
        return

    # --- GPIO setup ---
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(START_PIN,  GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SWITCH_MODE, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SWITCH1_PIN, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SWITCH2_PIN, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_R_PIN,  GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_G_PIN,  GPIO.OUT, initial=GPIO.LOW)

    print(f"[INFO] waiting for button (GPIO {START_PIN}), switch (GPIO {SWITCH_MODE})...")

    try:
        last_mode = None
        while True:
            set_led(red=False, green=True)
            mode = get_mode()
            alg = get_alg()

            # update LED when mode changes
            if mode != last_mode:
                set_led(mode)
                print(f"[INFO] mode: {mode}")
                last_mode = mode

            # start button
            if GPIO.input(START_PIN) == GPIO.LOW:
                print(f"[INFO] button pressed - starting orchestrator in mode: {mode}")
                set_led(red=True, green=True)
                Orchestrator(contrast_factor=CONTRAST_FAC, source=mode, mode=alg).run()
                set_led(red=False, green=True)
                while GPIO.input(START_PIN) == GPIO.LOW:
                    time.sleep(0.05)
                time.sleep(0.05)

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("[INFO] stopped")
        set_led(red=True, green=False)
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()