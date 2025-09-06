#ifndef __MEASURE_H__
#define __MEASURE_H__

#include "main.h"

extern uint16_t Measure_Buffer[128 * 3];
extern uint8_t Measure_OverFlag;

typedef enum
{
    NONE = 0,    // 无轨道
    STRAIGHT,    // 直线轨道
    BEND,        // 直角转弯轨道
    ARC,         // 圆弧轨道
} TRACK_TYPE;    // 轨道类型

void Measure_Start(void);
void Measure_Wait(void);
void Measure_GetSensorOutput(float *S1, float *S2, float *S3);

void Measure_AnalyzeTrack(TRACK_TYPE* track_type, float S_c, float S_r, float S_l, float K_c, float K_r, float K_l, float* theta, float* d, float* h);

float moving_average_filter(const uint16_t *data, int index, int size);

#endif
