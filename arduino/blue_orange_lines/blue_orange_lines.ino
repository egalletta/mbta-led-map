#include <Shifty.h>

Shifty reg_blue;
Shifty reg_orange;

const int NUM_BLUE_STATIONS = 12;
const int NUM_ORANGE_STATIONS = 20;



// setup the shift registers and begin serial transmission
void setup() {
  reg_blue.setBitCount(16);
  reg_blue.setPins(11, 12, 8);
  reg_orange.setBitCount(24);
  reg_orange.setPins(3, 4, 2);
  Serial.begin(115200);
}

void loop() {
  // wait for a string to be send via serial,
  // in the form of "[b | o]***...*", where * is either a "1" or "0"
  while(Serial.available() > 0 ){
    String str = Serial.readString();
    if (str.substring(0,1) == "b") { // blue line LEDs
      // turn on or off the appropriate LEDs hooked up to the shift register
      reg_blue.batchWriteBegin();
      for (int i = 1; i <= NUM_BLUE_STATIONS; i++) {
        if (str.substring(i, i+1) == "1") {
          reg_blue.writeBit((i - 1), HIGH);
        }
        else if (str.substring(i, i+1) == "0") {
          reg_blue.writeBit((i - 1), LOW);
        }
      }
      reg_blue.batchWriteEnd();
    }
    else if (str.substring(0,1) == "o") { // orange line LEDs
      reg_orange.batchWriteBegin();
      for (int i = 1; i <= NUM_ORANGE_STATIONS; i++) {
        if (str.substring(i, i+1) == "1") {
          reg_orange.writeBit((i - 1), HIGH);
        }
        else if (str.substring(i, i+1) == "0") {
          reg_orange.writeBit((i - 1), LOW);
        }
      }
      reg_orange.batchWriteEnd();
    }
  }
}
