Overview of all keys we can emulate with the current wiring. The "Shifted" column indicates that the shift key is also
required to be pressed at the same time.
TODO 1: complete
TODO 2: add to TypewriterDriver.py::CHAR_TO_PIN

| Non-Shifted  | Shifted (GPIO 2) | Pin   |                |
|--------------|------------------|-------|----------------|
| space        |                  | GPIO0 |                |
| ,            | dont care        | GPIO1 |                |
| 8            | *                | GPIO3 | is actually cr |
| 4            | $                | GPIO4 |                |
| 3            | #                | GPIO5 |                |
| 2            | @                | GPIO6 |                |
| =            | +                | GPIO7 |                |
| ;            | :                | GPIO8 |                |
| carry return |                  | GPIO9 |                |
