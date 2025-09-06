#ifndef __HMI_H__
#define __HMI_H__

#include "main.h"

extern uint8_t Serial_ReceiveBuffer[32];
extern uint8_t Serial_ReceiveReadyFlag;

void Serial_Init(void);

void Serial_SendData(int length);
void Serial_PrintDebug(int length);
void Serial_PrintString(const char *str);

int Serial_AddString(const char *str, int startIndex);
int Serial_AddInt(int value, int startIndex);
int Serial_AddDouble(double value, int startIndex, int precision);
int Serial_AddHex(uint32_t value, int startIndex);
int Serial_AddBin(uint32_t value, int startIndex);

int Serial_Pow(int base, int exp);

int Serial_ReceiveEquals(const char *str);

void Serial_HandleData(void);
void Serial_HandleOver(uint8_t response);

#endif
