#include <math.h>
#include <time.h>
#include <float.h>
#include <stdlib.h>
#include <string.h>

#include "adc.h"
#include "tim.h"
#include "measure.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif
#ifndef M_PI_2
#define M_PI_2 1.57079632679489661923f
#endif
#ifndef M_PI_4
#define M_PI_4 0.78539816339744830962f
#endif

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
 * @brief 定义方程组的残差函数
 * @param theta 轨道偏转角，弧度
 * @param d 轨道偏移距离，m
 * @param h 轨道高度，m
 * @param S_c 中间传感器输出，mV
 * @param S_r 右侧传感器输出，mV
 * @param S_l 左侧传感器输出，mV
 * @param K_c 中间传感器系数
 * @param K_r 右侧传感器系数
 * @param K_l 左侧传感器系数
 * @param f 输出残差数组
 */
void system_equations(float theta, float d, float h, float S_c, float S_r, float S_l, float K_c, float K_r, float K_l, float* f)
{
    // 方程1: f0 = S_c * √(d²+h²) - K_c sin(θ+π/2)
    f[0] = S_c * sqrtf(d*d + h*h) - K_c * sinf(theta + M_PI/2);

    // 方程2: f1 = S_r * √((d+0.065cosθ)²+h²) - K_r sin(arccos(√(2/3)cos(θ+π/4)))
    float cos_theta = cosf(theta);
    float d_adj_r = d + 0.065f * cos_theta;
    float inner_r = sqrtf(2.0f/3.0f) * cosf(theta + M_PI/4);
    inner_r = fmaxf(fminf(inner_r, 1.0f), -1.0f); // 钳位到[-1,1]
    f[1] = S_r * sqrtf(d_adj_r*d_adj_r + h*h) - K_r * sinf(acosf(inner_r));

    // 方程3: f2 = S_l * √((d-0.065cosθ)²+h²) - K_l sin(arccos(√(2/3)cos(θ-π/4)))
    float d_adj_l = d - 0.065f * cos_theta;
    float inner_l = sqrtf(2.0f/3.0f) * cosf(theta - M_PI/4);
    inner_l = fmaxf(fminf(inner_l, 1.0f), -1.0f); // 钳位到[-1,1]
    f[2] = S_l * sqrtf(d_adj_l*d_adj_l + h*h) - K_l * sinf(acosf(inner_l));
}

/**
 * @brief 简化估计算法
 * @param S_c 中间传感器输出，mV
 * @param S_r 右侧传感器输出，mV
 * @param S_l 左侧传感器输出，mV
 * @param K_c 中间传感器系数
 * @param K_r 右侧传感器系数
 * @param K_l 左侧传感器系数
 * @param theta 输出轨道偏转角，弧度
 * @param d 输出轨道偏移距离，m
 * @param h 输出轨道高度，m
 */
void simplified_estimation(float S_c, float S_r, float S_l, float K_c, float K_r, float K_l, float* theta, float* d, float* h)
{
    if (fabsf(S_r - S_l) < 1.0f) {
        *theta = 0.0f;
    }
    else
    {
        *theta = (S_r - S_l) / (S_c + S_r + S_l) * M_PI/2;
    }

    float avg_s = (S_c + S_r + S_l) / 3.0f;
    if (avg_s > 1.0f)
    {
        float dist = K_c / avg_s;
        *d = dist * cosf(*theta);
        *h = dist * sinf(*theta);
    }
    else
    {
        *d = 0.005f;
        *h = 0.005f;
    }

    *theta = fmaxf(fminf(*theta, M_PI/2), -M_PI/2);
    *d = fmaxf(fminf(*d, 0.01f), 0.0f);
    *h = fmaxf(fminf(*h, 0.01f), 0.0f);
}

/**
 * @brief 使用牛顿-拉夫森法求解非线性方程组
 * @param S_c 中间传感器输出，mV
 * @param S_r 右侧传感器输出，mV
 * @param S_l 左侧传感器输出，mV
 * @param K_c 中间传感器系数，mV
 * @param K_r 右侧传感器系数，mV
 * @param K_l 左侧传感器系数，mV
 * @param theta 输出轨道偏转角，弧度
 * @param d 输出轨道偏移距离，m
 * @param h 输出轨道高度，m
 * @param initial_theta 初始猜测的轨道偏转角，弧度
 * @param initial_d 初始猜测的轨道偏移距离，m
 * @param initial_h 初始猜测的轨道高度，m
 * @return 成功返回1，失败返回0
 */
int solve_system(float S_c, float S_r, float S_l, float K_c, float K_r, float K_l, float* theta, float* d, float* h, float initial_theta, float initial_d, float initial_h)
{
    const int max_iterations = 20;
    const float tolerance = 1e-4f;

    float x[3] = {initial_theta, initial_d, initial_h};
    float f[3];

    for (int iter = 0; iter < max_iterations; iter++)
    {
        system_equations(x[0], x[1], x[2], S_c, S_r, S_l, K_c, K_r, K_l, f);
        
        float norm = sqrtf(f[0]*f[0] + f[1]*f[1] + f[2]*f[2]);
        if (norm < tolerance)
        {
            *theta = x[0];
            *d = x[1];
            *h = x[2];
            return 1;
        }

        float alpha = 0.1f / (1.0f + iter*0.1f);

        const float h_val = 1e-4f;
        float f_theta[3], f_d[3], f_h[3];

        system_equations(x[0]+h_val, x[1], x[2], S_c, S_r, S_l, K_c, K_r, K_l, f_theta);
        system_equations(x[0], x[1]+h_val, x[2], S_c, S_r, S_l, K_c, K_r, K_l, f_d);
        system_equations(x[0], x[1], x[2]+h_val, S_c, S_r, S_l, K_c, K_r, K_l, f_h);

        for (int i = 0; i < 3; i++)
        {
            float grad_theta = (f_theta[i] - f[i]) / h_val;
            float grad_d = (f_d[i] - f[i]) / h_val;
            float grad_h = (f_h[i] - f[i]) / h_val;

            x[0] -= alpha * f[i] * grad_theta;
            x[1] -= alpha * f[i] * grad_d;
            x[2] -= alpha * f[i] * grad_h;
        }

        x[0] = fmaxf(fminf(x[0], M_PI/2), -M_PI/2);
        x[1] = fmaxf(fminf(x[1], 0.01f), 0.0f);
        x[2] = fmaxf(fminf(x[2], 0.01f), 0.0f);

        if (iter > 5 && norm > 10.0f) { return 0; }
    }

    return 0;
}

/**
 * @brief 解析轨道参数
 * @param track_type 轨道类型
 * @param S_c 中间传感器输出，mV
 * @param S_r 右侧传感器输出，mV
 * @param S_l 左侧传感器输出，mV
 * @param K_c 中间传感器系数
 * @param K_r 右侧传感器系数
 * @param K_l 左侧传感器系数
 * @param theta 输出轨道偏转角，角度制，-90°~90°
 * @param d 输出轨道偏移距离，mm
 * @param h 输出轨道高度，mm，>=0
 */
void Measure_AnalyzeTrack(TRACK_TYPE* track_type, float S_c, float S_r, float S_l, float K_c, float K_r, float K_l, float* theta, float* d, float* h)
{
    if (S_c > 500.0f && S_r < 10.0f && S_l < 10.0f)
    {
        *track_type = STRAIGHT;
    }
    else if (S_r < 2.0f && S_l > 250.0f)
    {
        *track_type = BEND;
    }
    else if (S_l > 20.0f && S_r < 3.0f && S_c < 2000.0f)
    {
        *track_type = ARC;
    }
    else
    {
        *track_type = NONE;
    }

    float angle_estimate = 0.0f;
    if (fabsf(S_r - S_l) > 1.0f)
    {
        angle_estimate = atan2f(S_r - S_l, S_c) * 0.5f;
        angle_estimate = fmaxf(fminf(angle_estimate, M_PI/2), -M_PI/2);
    }

    float avg_s = (S_c + S_r + S_l) / 3.0f;
    float dist_estimate = 0.0f;
    if (avg_s > 1.0f)
    {
        dist_estimate = fminf(0.01f, K_c / avg_s * 0.5f);
    }
    else
    {
        dist_estimate = 0.005f; // 默认值
    }

    float initial_theta = angle_estimate;
    float initial_d = dist_estimate * cosf(angle_estimate);
    float initial_h = dist_estimate * sinf(angle_estimate);

    int success = solve_system(S_c, S_r, S_l, K_c, K_r, K_l, theta, d, h, initial_theta, initial_d, initial_h);
    if (!success) { simplified_estimation(S_c, S_r, S_l, K_c, K_r, K_l, theta, d, h); }

    *theta = (*theta) * 180.0f / M_PI;
    *d = (*d) * 1000.0f;
    *h = fabsf((*h) * 1000.0f);
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
