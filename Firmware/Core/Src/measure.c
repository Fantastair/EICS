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
    // HAL_ADC_Stop_DMA(&hadc1);
    // HAL_ADCEx_Calibration_Start(&hadc1);
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

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
    if (hadc->Instance == ADC1)
    {
        HAL_TIM_Base_Stop(&htim3);
        Measure_OverFlag = 1;
    }
}
