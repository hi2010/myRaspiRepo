#include <SoftSpi.hpp>

void SoftSpi::init(){
    // out
    pinMode(SS_PIN, OUTPUT);
    digitalWrite(SS_PIN, HIGH);
    pinMode(CK_PIN, OUTPUT);
    digitalWrite(CK_PIN, HIGH);
    pinMode(SDI_PIN, OUTPUT);
    digitalWrite(SDI_PIN, LOW);
    // in
    pinMode(SDO_PIN, INPUT);
}

static const int DELUS = 100;
// all timings are in ns -> use delay of microseconds
uint8_t SoftSpi::transfer(uint8_t buffer, bool useSSPin){
    uint8_t byte_in = 0;
    if (useSSPin) {
        // ss low
        digitalWrite(SS_PIN, LOW);
        delayMicroseconds(DELUS);
    }

    uint8_t bits = 8;
    do {
        digitalWrite(CK_PIN, LOW);
        digitalWrite(SDI_PIN, buffer & 0x80);
        delayMicroseconds(DELUS);
        //DELAY_NS(125);
        digitalWrite(CK_PIN, HIGH);
        delayMicroseconds(DELUS);
        buffer <<= 1;        // little setup time
        buffer |= (digitalRead(SDO_PIN) != 0);
        delayMicroseconds(DELUS);
    } while (--bits);
    delayMicroseconds(DELUS);
    //DELAY_NS(125);

    if (useSSPin) {
        // ss high
        digitalWrite(SS_PIN, HIGH);
        delayMicroseconds(DELUS);
    }
    return byte_in;
}

// msb first -> idx high to low
void SoftSpi::transfer(uint8_t *buffer, uint8_t size){
    digitalWrite(SS_PIN, LOW);
    delayMicroseconds(DELUS);
    for (uint8_t i = size; i; i--) {
        uint8_t tempByte = SoftSpi::transfer(buffer[i-1]);
        buffer[i-1] = tempByte;
    }
    digitalWrite(SS_PIN, HIGH);
    delayMicroseconds(DELUS);
}