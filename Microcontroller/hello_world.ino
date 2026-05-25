/*
  IBM Wheelwriter hack
  Pin 0: connected through MOSFET to Wheelwriter bus
         Will pull down the bus when set to zero
  Pin 2: ALSO connected to the bus, but listens instead of 
         sending data
 */

// on an Arduino Nano, ATmega328, the following will delay roughly 5.25us
// TODO: adjust for model we use
#define pulseDelay() { for (int i=0;i<16;i++) { __asm__ __volatile__("nop\n\t"); } }

void setup()
{
    // Pin that will trigger the bus
   pinMode(2,OUTPUT); 
   // TODO: other pins? idk if needed for HelloWorld tho
//   pinMode(3, INPUT); // listening pin
//   pinMode(4, INPUT_PULLUP); // for the button

   // start the input pin off, meaning the bus is high, normal state
   // (PORTD is the port with digital pins 0 to 7.
   // Manipulating it directly is faster than setting pins the usual way.
  // For more info, see https://docs.arduino.cc/retired/hacking/software/PortManipulation/ )
     PORTD &= 0b11111011;



}

void loop()
{
    helloWorld();
}

void helloWorld()
{
    // TODO find out if needed (apparently this is a built in function?) turn off interrupts so we don't get disturbed
    noInterrupts();

    // TODO rest of the code (Reference ll. )
}