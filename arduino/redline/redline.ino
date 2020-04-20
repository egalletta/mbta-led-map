#include <Shifty.h>

Shifty reg_red;

const int NUM_red_STATIONS = 22;



// setup the shift registers and begin serial transmission
void setup() {
  reg_red.setBitCount(24);
  reg_red.setPins(11, 12, 8);
  
  Serial.begin(115200);
}

// the loop function runs over and over again forever
void loop() {
  // wait for a string to be send via serial,
  // in the form of "r***...*", where * is either a "1" or "0"
  while(Serial.available() > 0 ){
    String str = Serial.readString();
    if (str.substring(0,1) == "r") {
      clear_lights();
      reg_red.batchWriteBegin();
      for (int i = 1; i <= NUM_red_STATIONS; i++) {
        if (str.substring(i, i+1) == "1") {
          reg_red.writeBit((i - 1), HIGH);
        }
        else if (str.substring(i, i+1) == "0") {
          reg_red.writeBit((i - 1), LOW);
        }
      }
      reg_red.batchWriteEnd();
    }
  }
}

void clear_lights() {
  for (int i = 0; i < NUM_red_STATIONS; i++) {
    reg_red.writeBit(i, LOW);
  }
}
