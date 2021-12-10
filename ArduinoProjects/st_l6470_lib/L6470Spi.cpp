#include "L6470Spi.hpp"
#include <SoftSpi.hpp>

#include <Arduino.h>
auto spi = SoftSpi();

// using other pin as sspin for more control
static const uint8_t SS_PIN = 9;
static const uint8_t MOSI_PIN = 11;
static const uint8_t MISO_PIN = 12;
static const uint8_t SCK_PIN = 13;

// SPI.transfer(buffer, size) -> from arduino page
uint8_t buffer4Byte[4];
uint8_t buffer3Byte[3];
uint8_t buffer2Byte[2];
uint8_t bufferByte;

void initSpi(){
    spi.init();
}

void setParam(uint8_t reg, uint8_t *value, uint8_t size){
    buffer4Byte[3] = 0b00000000 | reg;
    for (uint8_t i = size-1; i; i--){
        buffer4Byte[i] = value[size-i-1];
    }
    spi.transfer(buffer4Byte, size);
}

uint8_t *getParam(uint8_t reg, uint8_t size){
    buffer4Byte[3] = 0b00100000 | reg;
    buffer4Byte[2] = 0x00;
    buffer4Byte[1] = 0x00;
    buffer4Byte[0] = 0x00;
    spi.transfer(buffer4Byte, size);
    return buffer4Byte;
}

bool initDevice(){
    // stall th
    buffer2Byte[1] = STALL_TH_REG;
    buffer2Byte[0] = 0x2a;
    spi.transfer(buffer2Byte, 2);
    // acceleration
    buffer3Byte[2] = ACC_REG;
    buffer3Byte[1] = 0x00;
    buffer3Byte[0] = 0x05;
    spi.transfer(buffer3Byte, 3);
    // max speed
    buffer3Byte[2] = MAX_SPEED_REG;
    buffer3Byte[1] = 0x00;
    buffer3Byte[0] = 0x24;
    spi.transfer(buffer3Byte, 3);
    // kval acc
    buffer2Byte[1] = KVAL_ACC_REG;
    buffer2Byte[0] = 0x4F;
    spi.transfer(buffer2Byte, 2);
    // kval run
    buffer2Byte[1] = KVAL_RUN_REG;
    buffer2Byte[0] = 0x4F;
    spi.transfer(buffer2Byte, 2);
    // kval dec
    buffer2Byte[1] = KVAL_DEC_REG;
    buffer2Byte[0] = 0x4E;
    spi.transfer(buffer2Byte, 2);
    return true; // TODO: check written values for correctness -> res is bool
}

void resetDevice(){
    spi.transfer(0xC0);
    delayMicroseconds(10);
   // initDevice();
}

uint8_t *getStatus(){
    // resets flags
    buffer3Byte[2] = 0xD0;
    buffer3Byte[1] = 0x00;
    buffer3Byte[0] = 0x00;
    spi.transfer(buffer3Byte, 3);
    return buffer3Byte;
}


void softStop(){
    spi.transfer(0xB0);
}

void hardStop(){
    spi.transfer(0xB8);
}

void softHiZ(){
    spi.transfer(0xA8);
}

void goHome(){
    spi.transfer(0x70);
}

uint8_t *readStatus(){
    // dunno godda watch instr
    buffer3Byte[2] = 0x39; // cmd
    buffer3Byte[1] = 0x00; // response
    buffer3Byte[0] = 0x00; // response
    spi.transfer(buffer3Byte, 3);
    return buffer3Byte;
}

// is locking
void stopOnStall(){
    uint8_t *stat = readStatus();
    while(((stat[0] & 0x40) == 0) || ((stat[0] & 0x20) == 0)){
        stat = readStatus();
    }
    hardStop();
    delay(1);
    getStatus();
}

void run(uint8_t direction, uint32_t speed){
    if (direction){
        buffer4Byte[3] = 0x50;
    } else {
        buffer4Byte[3] = 0x51;
    }
    buffer4Byte[2] = (speed >> 16) & 0xFF;
    buffer4Byte[1] = (speed >> 8) & 0xFF;
    buffer4Byte[0] = speed & 0xFF;
    spi.transfer(buffer4Byte, 4);
}

void goTo(uint32_t position){  // position is 24 bit
    buffer4Byte[3] = 0x60;
    buffer4Byte[2] = (position >> 16) & 0x3F;
    buffer4Byte[1] = (position >> 8) & 0xFF;
    buffer4Byte[0] = position & 0xFF;
    spi.transfer(buffer4Byte, 4);
}

void move(uint8_t direction, uint32_t nStep){ // nStep is 24 bit
    if (direction){
        buffer4Byte[3] = 0x41;
    } else {
        buffer4Byte[3] = 0x40;
    }
    buffer4Byte[2] = (nStep >> 16) & 0x3F;
    buffer4Byte[1] = (nStep >> 8) & 0xFF;
    buffer4Byte[0] = nStep & 0xFF;
    spi.transfer(buffer4Byte, 4);
}