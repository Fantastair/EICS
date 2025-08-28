#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <time.h>

#include "adc.h"
#include "tim.h"
#include "measure.h"

#define M_PI 3.14159265358979323846f
#define S_OFFSET 0.06f
#define MAX_ITER 50
#define TOLERANCE 1e-5f
#define NUM_RANDOM_STARTS 10

typedef struct {
    float theta;
    float d;
    float h;
    float error;
} PositionParams;

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
void Measure_GetSensorOutput(float *S1, float *S2, float *S3)
{
    uint16_t channel1[128];
    uint16_t channel2[128];
    uint16_t channel3[128];
    float sum1 = 0.0f, sum2 = 0.0f, sum3 = 0.0f;

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
 * @brief 计算误差函数
 * @param theta 偏转角度（弧度）
 * @param d 水平偏移（米）
 * @param h 高度（米）
 * @param s_c 传感器C的实际读数
 * @param s_r 传感器R的实际读数
 * @param s_l 传感器L的实际读数
 * @return 计算得到的误差值
 */
float calculate_error(float theta, float d, float h, float s_c, float s_r, float s_l)
{
    float denom_c = d*d + h*h;
    float denom_l = (d - S_OFFSET * cosf(theta)) * (d - S_OFFSET * cosf(theta)) + h*h;
    float denom_r = (d + S_OFFSET * cosf(theta)) * (d + S_OFFSET * cosf(theta)) + h*h;
    
    if (denom_c < 1e-10f) denom_c = 1e-10f;
    if (denom_l < 1e-10f) denom_l = 1e-10f;
    if (denom_r < 1e-10f) denom_r = 1e-10f;
    
    float term_c = h * fabsf(cosf(theta)) / denom_c;
    float term_l = h * fabsf(cosf(theta - M_PI/4.0f)) / denom_l;
    float term_r = h * fabsf(cosf(theta + M_PI/4.0f)) / denom_r;
    
    float error = (term_c - s_c) * (term_c - s_c) + (term_l - s_l) * (term_l - s_l) + (term_r - s_r) * (term_r - s_r);
    
    return error;
}

/**
 * @brief 生成随机浮点数
 * @param min 最小值
 * @param max 最大值
 * @return 生成的随机浮点数
 */
float random_float(float min, float max)
{
    return min + (max - min) * ((float)rand() / 0x7fffff);
}

/**
 * @brief 多起点优化
 * @param s_c 传感器C的实际读数
 * @param s_r 传感器R的实际读数
 * @param s_l 传感器L的实际读数
 * @return 最优位置参数
 */
PositionParams multi_start_optimization(float s_c, float s_r, float s_l)
{
    PositionParams best_params = {0, 0, 0.03f, FLT_MAX};
    
    for (int i = 0; i < NUM_RANDOM_STARTS; i++)
    {
        PositionParams start;
        start.theta = random_float(-M_PI/4.0f, M_PI/4.0f);
        start.d = random_float(-0.05f, 0.05f);
        start.h = random_float(0.01f, 0.05f);
        start.error = calculate_error(start.theta, start.d, start.h, s_c, s_r, s_l);
        
        PositionParams current = start;
        float step_size = 0.01f;
        int improved;
        
        for (int iter = 0; iter < MAX_ITER; iter++)
        {
            improved = 0;

            float directions[6][3] = {
                {step_size, 0, 0}, {-step_size, 0, 0},
                {0, step_size, 0}, {0, -step_size, 0},
                {0, 0, step_size}, {0, 0, -step_size}
            };
            
            for (int j = 0; j < 6; j++)
            {
                PositionParams candidate;
                candidate.theta = current.theta + directions[j][0];
                candidate.d = current.d + directions[j][1];
                candidate.h = current.h + directions[j][2];
                
                if (candidate.theta < -M_PI/4.0f) candidate.theta = -M_PI/4.0f;
                if (candidate.theta > M_PI/4.0f) candidate.theta = M_PI/4.0f;
                if (candidate.d < -0.05f) candidate.d = -0.05f;
                if (candidate.d > 0.05f) candidate.d = 0.05f;
                if (candidate.h < 0.01f) candidate.h = 0.01f;
                if (candidate.h > 0.05f) candidate.h = 0.05f;
                
                candidate.error = calculate_error(candidate.theta, candidate.d, candidate.h, s_c, s_r, s_l);
                
                if (candidate.error < current.error)
                {
                    current = candidate;
                    improved = 1;
                }
            }

            if (!improved)
            {
                step_size *= 0.5f;
                if (step_size < 1e-5f) break;
            }
        }

        if (current.error < best_params.error)
        {
            best_params = current;
        }
    }
    
    return best_params;
}

/**
 * @brief 解析传感器数据
 * @param S_c 传感器C的原始读数
 * @param S_r 传感器R的原始读数
 * @param S_l 传感器L的原始读数
 * @param K 归一化系数
 * @return 解析后的位置信息
 */
PositionParams parse_sensor_data(float S_c, float S_r, float S_l, float K)
{
    float s_c = S_c / K;
    float s_r = S_r / K;
    float s_l = S_l / K;

    PositionParams result = multi_start_optimization(s_c, s_r, s_l);

    return result;
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
void Measure_AnalyzeTrack(float S1, float S2, float S3, TRACK_TYPE *track_type, float *angle, float *distance, float *height)
{
    if (S1 < 1 && S2 < 1 && S3 < 1)    // 传感器无数据
    {
        *track_type = NONE;
        *angle = 0.0f;
        *distance = 0.0f;
        *height = 0.0f;
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
    PositionParams params = parse_sensor_data(S2, S3, S1, 15.0f);
    *angle = params.theta * 180.0f / M_PI;
    *distance = params.d;
    *height = params.h;
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
float moving_average_filter(const uint16_t *data, int index, int size)
{
    int window_size = 3;
    int start_idx = (index - window_size / 2) > 0 ? (index - window_size / 2) : 0;
    int end_idx = (index + window_size / 2 + 1) < size ? (index + window_size / 2 + 1) : size;
    float sum = 0.0f;
    int count = 0;

    for (int i = start_idx; i < end_idx; i++) {
        sum += data[i];
        count++;
    }
    
    return sum / count;
}
