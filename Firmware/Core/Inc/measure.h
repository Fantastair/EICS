#ifndef __MEASURE_H__
#define __MEASURE_H__

#include "main.h"

extern uint16_t Measure_Buffer[128 * 3];
extern uint8_t Measure_OverFlag;

void Measure_Start(void);
void Measure_Wait(void);

#endif
