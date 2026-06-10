import time
from Orchestrator import Orchestrator, CONTRAST_FAC, MODE_STANDARD, MODE_ARTISTIC

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False

START_PIN = 27 # button: start
SWITCH_PIN = 22 # switch: switch mode (HIGH = standard, LOW = artistic)
LED_R_PIN = 23 # button: LED red = standard mode
LED_G_PIN = 24 # button: LED green = artistic mode

def get_mode() -> str:
    return MODE_ARTISTIC if GPIO.input(SWITCH_PIN) == GPIO.LOW else MODE_STANDARD

def set_led(mode: str) -> None:
    GPIO.output(LED_R_PIN, GPIO.HIGH if mode == MODE_STANDARD else GPIO.LOW)
    GPIO.output(LED_G_PIN, GPIO.HIGH if mode == MODE_ARTISTIC else GPIO.LOW)

def main():
    #for local testing
    if not GPIO_AVAILABLE:
        print("[WARN] simulation - press enter to start")
        mode = MODE_STANDARD
        while True:
            user_input = input()
            if user_input.strip() in (MODE_STANDARD, MODE_ARTISTIC):
                mode = user_input.strip()
                print(f"[SIM] set mode to: {mode}")
            else:
                print(f"[SIM] button pressed - starting orchestrator in mode: {mode}")
                Orchestrator(contrast_factor=CONTRAST_FAC, mode=mode).run()
        return

    # --- GPIO setup ---
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(START_PIN,  GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SWITCH_PIN, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_R_PIN,  GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_G_PIN,  GPIO.OUT, initial=GPIO.LOW)

    print(f"[INFO] waiting for button (GPIO {START_PIN}), switch (GPIO {SWITCH_PIN})...")

    try:
        last_mode = None
        while True:
            mode = get_mode()

            # update LED when mode changes
            if mode != last_mode:
                set_led(mode)
                print(f"[INFO] mode: {mode}")
                last_mode = mode

            # start button
            if GPIO.input(START_PIN) == GPIO.LOW:
                print(f"[INFO] button pressed - starting orchestrator in mode: {mode}")
                Orchestrator(contrast_factor=CONTRAST_FAC, mode=mode).run()
                while GPIO.input(START_PIN) == GPIO.LOW:
                    time.sleep(0.05)
                time.sleep(0.05)

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("[INFO] stopped")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()