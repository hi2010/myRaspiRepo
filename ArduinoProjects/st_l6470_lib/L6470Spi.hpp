#pragma once

#ifndef _L6470Spi_H_
#define _L6470Spi_H_

#include <Arduino.h>

// register adresses
// datasheet 9.1, p.: 40/41
//                                      len:
static const uint8_t ABS_POS_REG = 0x01;    // 22
static const uint8_t EL_POS_REG = 0x02;     //  9
static const uint8_t MARK_REG   = 0x03;     // 22
static const uint8_t SPEED_REG  = 0x04;     // 20
static const uint8_t ACC_REG    = 0x05;     // 12
static const uint8_t DEC_REG    = 0x06;     // 12  had to add reg cause deg is keyword??
static const uint8_t MAX_SPEED_REG = 0x07;  // 10
static const uint8_t MIN_SPEED_REG = 0x08;  // 13
static const uint8_t FS_SPD_REG = 0x15;     // 10
static const uint8_t KVAL_HOLD_REG = 0x09;  //  8
static const uint8_t KVAL_RUN_REG  = 0x0A;  //  8
static const uint8_t KVAL_ACC_REG  = 0x0B;  //  8
static const uint8_t KVAL_DEC_REG  = 0x0C;  //  8
static const uint8_t INT_SPEED_REG = 0x0D;  // 14
static const uint8_t ST_SLP_REG = 0x0E;     //  8
static const uint8_t FN_SLP_ACC_REG = 0x0F; //  8
static const uint8_t FN_SLP_DEC_REG = 0x10; //  8
static const uint8_t K_THERM_REG = 0x11;    //  4
static const uint8_t ADC_OUT_REG = 0x12;    //  5
static const uint8_t OCD_TH_REG  = 0x13;    //  4
static const uint8_t STALL_TH_REG = 0x14;   //  7
static const uint8_t STEP_MODE_REG = 0x16;  //  8
static const uint8_t ALARM_EN_REG = 0x17;   //  8
static const uint8_t CONFIG_REG = 0x18;     // 16
static const uint8_t STATUS_REG = 0x19;     // 16

void setParam(uint8_t reg, uint8_t *value, uint8_t size);
uint8_t *getParam(uint8_t reg, uint8_t size);

void initSpi();
void resetDevice();
bool initDevice();
void softStop();
void hardStop();
void softHiZ();
void goHome();
uint8_t *readStatus();
uint8_t *getStatus(); // resets registers
void stopOnStall();
void run(uint8_t direction, uint32_t speed); // speed is 24 bit
void goTo(uint32_t position);  // position is 19 bit
void move(uint8_t direction, uint32_t nStep); // nStep is 19 bit

#endif // _L6470Spi_H_
