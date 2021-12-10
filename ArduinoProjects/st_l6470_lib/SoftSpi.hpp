#pragma once

#ifndef _SOFTSpi_H_
#define _SOFTSpi_H_

#include <Arduino.h>

class SoftSpi {
public:
    uint8_t SS_PIN = 8;
    uint8_t CK_PIN = 11;
    uint8_t SDI_PIN = 10;
    uint8_t SDO_PIN = 12;
    void init();
    uint8_t transfer(uint8_t buffer, bool useSSPin=true);
    void transfer(uint8_t *buffer, uint8_t size);
};

#endif // _SOFTSpi_H_