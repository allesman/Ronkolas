// on an Arduino Nano, ATmega328, the following will delay roughly 5.25us
// TODO: adjust for model we use
#define pulseDelay() { for (int i=0;i<16;i++) { __asm__ __volatile__("nop\n\t"); } }

#define PIN2_MASK 0b00000100
#define PIN3_MASK 0b00001000

void toggleInput(const bool turnOn) {
    // PORTD is the port with digital pins 0 to 7, with the mask we are changing pin 2 only.
    // Manipulating it directly like this is faster than setting pins the usual way.
    // For more info, see https://docs.arduino.cc/retired/hacking/software/PortManipulation/

    // CAREFUL: what the pin is set to is the opposite of what ends up at the typewriter bus (cause its connected via a transistor)
    if (turnOn) {
        // set the pin to 0 -> set the pin low -> bus pulls high -> turn on
        PORTD &= ~PIN2_MASK;
    } else {
        // set the pin to 1 -> set the pin high -> bus pulls low -> turn off
        PORTD |= PIN2_MASK;
    }
    pulseDelay();
}

void sendByte(const int _byte) {
    /* send nine bits
     * with a zero initial
    */

    // built in function to turn off interrupts so we don't get disturbed
    noInterrupts();

    // zero initial bit
    toggleInput(false);

    // the other nine bits (actual data)
    //we start on the little end (right side) and work our way left
    int bitMask = 0b000000001;
    // tell the compiler to unroll the loop for better performance
#pragma GCC unroll 9
    for (int i = 0; i < 9; i++) {
        // select bit to process
        const bool _bit = (_byte & bitMask) != 0;
        // process bit by setting pin
        toggleInput(_bit);
        // update bitMask for next bit (shift left)
        bitMask <<= 1;
    }

    // reset to idle state
    toggleInput(true);

    // Interrupts back on
    interrupts();
}

void sendByteAndWait(const int _byte) {
    sendByte(_byte);
    // TODO: waiting logic Reference ll 807ff, https://github.com/tofergregg/IBM-Wheelwriter-Hack/blob/master/software/WheelwriterControlNano/WheelwriterControlNano.ino
    
    while (PIND & PIN3_MASK) {} // line goes low
    while (!(PIND & PIN3_MASK)) {} // line goes high

    delayMicroseconds(450);
}

void printRawChar(int rawChar) {
    // Bus Protocol Headers
    sendByteAndWait(0b100100001);
    sendByteAndWait(0b000001011);
    sendByteAndWait(0b100100001);
    sendByteAndWait(0b000000011);

    // Actual Char
    sendByteAndWait(rawChar);
}

void setup() {
    // Pin that will trigger the bus
    pinMode(2, OUTPUT);
    // TODO: other pins? likely not needed for HelloWorld tho
    //   pinMode(3, INPUT); // listening for wheelwriter responses
    //   pinMode(4, INPUT_PULLUP); // for user input button?

    // idle state (bus high)
    toggleInput(true);

    // inshallah please work
    printRawChar('A');
}

void loop() {
    printRawChar('A');
}
