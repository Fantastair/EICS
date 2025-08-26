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
void Measure_GetSensorOutput(double *S1, double *S2, double *S3);

void Measure_AnalyzeTrack(double S1, double S2, double S3, TRACK_TYPE *track_type, double *angle, double *distance, double *height);

double moving_average_filter(const uint16_t *data, int index, int size);

#endif
