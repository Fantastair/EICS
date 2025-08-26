#include "adc.h"
#include "tim.h"
#include "measure.h"

uint16_t Measure_Buffer[128 * 3];    // 测量数据缓冲区
uint8_t Measure_OverFlag = 0;        // 测量完成标志

/**
 * @brief 启动测量
 */
void Measure_Start(void)
{
    HAL_ADC_Start_DMA(&hadc1, (uint32_t *)Measure_Buffer, sizeof(Measure_Buffer) / 2);
    HAL_TIM_Base_Start(&htim3);
}

/**
 * @brief 等待测量完成
 */
void Measure_Wait(void)
{
    while (Measure_OverFlag == 0);
    Measure_OverFlag = 0;
}

/**
 * @brief 获取测量结果
 * @param S1 通道1测量结果，mV
 * @param S2 通道2测量结果，mV
 * @param S3 通道3测量结果，mV
 */
void Measure_GetSensorOutput(double *S1, double *S2, double *S3)
{
    uint16_t channel1[128];
    uint16_t channel2[128];
    uint16_t channel3[128];
    double sum1 = 0.0, sum2 = 0.0, sum3 = 0.0;

    for (int i = 0; i < 128; i++)
    {
        channel1[i] = Measure_Buffer[i * 3];
        channel2[i] = Measure_Buffer[i * 3 + 1];
        channel3[i] = Measure_Buffer[i * 3 + 2];
    }
    for (int i = 0; i < 128; i++)
    {
        sum1 += moving_average_filter(channel1, i, 128);
        sum2 += moving_average_filter(channel2, i, 128);
        sum3 += moving_average_filter(channel3, i, 128);
    }

    *S1 = sum1 / 128.0 / 4095.0 * 3300;
    *S2 = sum2 / 128.0 / 4095.0 * 3300;
    *S3 = sum3 / 128.0 / 4095.0 * 3300;
}

/**
 * @brief 分析轨道类型
 * @param S1 通道1电压值
 * @param S2 通道2电压值
 * @param S3 通道3电压值
 * @param track_type 轨道类型
 * @param angle 角度
 * @param distance 距离
 * @param height 高度
 */
void Measure_AnalyzeTrack(double S1, double S2, double S3, TRACK_TYPE *track_type, double *angle, double *distance, double *height)
{
    if (S1 < 1 && S2 < 1 && S3 < 1)    // 传感器无数据
    {
        *track_type = NONE;
        *angle = 0.0;
        *distance = 0.0;
        *height = 0.0;
        return;
    }
    else if (S1 < 100 && S3 < 100 && S2 > 200)    // 直线轨道
    {
        *track_type = STRAIGHT;
    }
    else if (S1 > 100 && S3 < 100 && S2 > 200)    // 直角转弯轨道
    {
        *track_type = BEND;
    }
    else if (S1 > 50 && S3 < 100 && S2 > 200)    // 圆弧轨道
    {
        *track_type = ARC;
    }
    *angle = 0.0;
    *distance = 0.0;
    *height = 0.0;
}

/**
 * @brief ADC转换完成回调函数
 * @param hadc ADC句柄
 */
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
    if (hadc->Instance == ADC1)
    {
        HAL_TIM_Base_Stop(&htim3);
        HAL_ADC_Stop_DMA(&hadc1);
        Measure_OverFlag = 1;
    }
}

/**
 * @brief 移动平均滤波
 * @param data 输入数据
 * @param index 当前索引
 * @param size 数据大小
 * @return 滤波后的值
 */
double moving_average_filter(const uint16_t *data, int index, int size)
{
    int window_size = 3;
    int start_idx = (index - window_size / 2) > 0 ? (index - window_size / 2) : 0;
    int end_idx = (index + window_size / 2 + 1) < size ? (index + window_size / 2 + 1) : size;    
    double sum = 0.0;
    int count = 0;

    for (int i = start_idx; i < end_idx; i++) {
        sum += data[i];
        count++;
    }
    
    return sum / count;
}
