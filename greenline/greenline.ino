#include <Shifty.h>

Shifty reg_green;

const int NUM_green_STATIONS = 66;



// setup the shift registers and begin serial transmission
void setup() {
  reg_green.setBitCount(72);
  reg_green.setPins(11, 12, 8);
  
  Serial.begin(9600);
}

// the loop function runs over and over again forever
void loop() {
  // wait for a string to be send via serial,
  // in the form of "g***...*", where * is either a "1" or "0"
  while(Serial.available() > 0 ){
    String str = Serial.readString();
    if (str.substring(0,1) == "g") {
      reg_green.batchWriteBegin();
      for (int i = 1; i <= NUM_green_STATIONS; i++) {
        if (str.substring(i, i+1) == "1") {
          reg_green.writeBit((i - 1), HIGH);
        }
        else if (str.substring(i, i+1) == "0") {
          reg_green.writeBit((i - 1), LOW);
        }
      }
      reg_green.batchWriteEnd();
    }
  }
}
