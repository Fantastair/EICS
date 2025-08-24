#include "main.h"
#include "math.h"
#include "usart.h"
#include "serial.h"

uint8_t Serial_DataBuffer[128];            // 发送指令缓冲区
uint8_t Serial_ReceiveBuffer[32] = {0};    // 接收数据缓冲区
uint8_t Serial_ReceiveIndex = 0;           // 接收数据索引
uint8_t Serial_ReceiveReadyFlag = 0;       // 接收完成标志

/**
 * @brief 初始化串口
 */
void Serial_Init(void)
{
    HAL_UART_Receive_IT(&huart1, Serial_ReceiveBuffer, 1);
}

/**
 * @brief 发送数据包到 Serial
 * @param length 数据包的长度
 */
void Serial_SendData(int length)
{
    Serial_DataBuffer[length] = Serial_DataBuffer[length + 1] = Serial_DataBuffer[length + 2] = 0xFF;
    HAL_UART_Transmit(&huart1, Serial_DataBuffer, length + 3, HAL_MAX_DELAY);
}

/**
 * @brief 打印调试信息到 Serial
 * @param length 指令的长度
 */
void Serial_PrintDebug(int length)
{
    HAL_UART_Transmit(&huart1, (uint8_t *)">>> debug: ", 11, HAL_MAX_DELAY);
    HAL_UART_Transmit(&huart1, Serial_DataBuffer, length, HAL_MAX_DELAY);
    HAL_UART_Transmit(&huart1, (uint8_t *)"\xff\xff\xff", 3, HAL_MAX_DELAY);
}

/**
 * @brief 打印字符串到 Serial
 * @param str 要打印的字符串
 */
void Serial_PrintString(const char *str)
{
    int index = 0;
    index = Serial_AddString(str, index);
    Serial_PrintDebug(index);
}

/**
 * @brief 将指令添加到缓冲区
 * @param str 要添加的字符串
 * @param startIndex 缓冲区的起始索引
 * @return 返回下一个可用的索引位置。
 */
int Serial_AddString(const char *str, int startIndex)
{
    int i = 0;
    while (str[i] != '\0')
    {
        Serial_DataBuffer[i + startIndex] = str[i];
        i++;
    }
    return startIndex + i;
}

/**
 * @brief 将整数添加到缓冲区
 * @param value 要添加的整数值
 * @param startIndex 缓冲区的起始索引
 * @return 返回下一个可用的索引位置。
 */
int Serial_AddInt(int value, int startIndex)
{
    int i = 0;
    if (value < 0)
    {
        Serial_DataBuffer[startIndex++] = '-';
        value = -value;
    }

    // 将整数转换为字符串
    if (value == 0)
    {
        Serial_DataBuffer[startIndex++] = '0';
        return startIndex;
    }

    int temp = value;
    while (temp > 0)
    {
        temp /= 10;
        i++;
    }

    for (int j = i - 1; j >= 0; j--)
    {
        Serial_DataBuffer[startIndex + j] = (value % 10) + '0';
        value /= 10;
    }

    return startIndex + i;
}

/**
 * @brief 将双精度浮点数添加到缓冲区
 * @param value 要添加的双精度浮点数值
 * @param startIndex 缓冲区的起始索引
 * @param precision 小数点后保留的位数
 * @return 返回下一个可用的索引位置。
 */
int Serial_AddDouble(double value, int startIndex, int precision)
{
    // 1. 处理负号并记录原始符号
    int isNegative = (value < 0);
    double absValue = fabs(value);

    // 2. 计算四舍五入因子
    double factor = Serial_Pow(10.0, precision);

    // 3. 整体四舍五入（避免分离计算导致的进位错误）
    double rounded = round(absValue * factor) / factor;

    // 4. 重新分离整数和小数部分
    double integerPart;
    double fractionalPart = modf(rounded, &integerPart);

    // 5. 处理负号输出
    if (isNegative)
    {
        Serial_DataBuffer[startIndex++] = '-';
    }

    // 6. 输出整数部分
    startIndex = Serial_AddInt((int)integerPart, startIndex);

    // 7. 输出小数点
    Serial_DataBuffer[startIndex++] = '.';

    // 8. 处理小数部分（考虑四舍五入和补零）
    if (precision > 0)
    {
        // 获取精确的小数部分整数表示
        int fracInt = (int)round(fractionalPart * factor);

        // 处理进位产生的整数部分变化
        if (fracInt >= (int)factor)
        {
            fracInt = 0;
            // 注意：整数部分已在第4步通过modf处理进位
        }

        // 按精度位数补零
        int divisor = (int)factor / 10;
        for (int i = 0; i < precision; i++)
        {
            int digit = (divisor > 0) ? (fracInt / divisor) % 10 : 0;
            Serial_DataBuffer[startIndex++] = '0' + digit;
            divisor /= 10;
        }
    }
    return startIndex;
}

/**
 * @brief 将十六进制数添加到缓冲区
 * @param value 要添加的十六进制数值
 * @param startIndex 缓冲区的起始索引
 * @return 返回下一个可用的索引位置。
 */
int Serial_AddHex(uint32_t value, int startIndex)
{
    int i = 0;
    static char hexDigits[] = "0123456789ABCDEF";
    startIndex = Serial_AddString("0x", startIndex);

    // 处理0的情况
    if (value == 0)
    {
        Serial_DataBuffer[startIndex++] = '0';
        return startIndex;
    }

    // 计算十六进制数的长度
    uint32_t temp = value;
    while (temp > 0)
    {
        temp /= 16;
        i++;
    }

    // 将十六进制数转换为字符串
    for (int j = i - 1; j >= 0; j--)
    {
        Serial_DataBuffer[startIndex + j] = hexDigits[value % 16];
        value /= 16;
    }

    return startIndex + i;
}

/**
 * @brief 将二进制数添加到缓冲区
 * @param value 要添加的二进制数值
 * @param startIndex 缓冲区的起始索引
 * @return 返回下一个可用的索引位置。
 */
int Serial_AddBin(uint32_t value, int startIndex)
{
    int i = 0;
    startIndex = Serial_AddString("0b", startIndex);

    // 处理0的情况
    if (value == 0)
    {
        Serial_DataBuffer[startIndex++] = '0';
        return startIndex;
    }

    // 计算二进制数的长度
    uint32_t temp = value;
    while (temp > 0)
    {
        temp /= 2;
        i++;
    }

    // 将二进制数转换为字符串
    for (int j = i - 1; j >= 0; j--)
    {
        Serial_DataBuffer[startIndex + j] = (value % 2) + '0';
        value /= 2;
    }

    return startIndex + i;
}

/**
 * @brief 完成数据处理，可以接收新的数据
 */
void Serial_HandleOver(uint8_t response)
{
    Serial_ReceiveReadyFlag = 0;
    if (response == 1)
    {
        HAL_UART_Transmit(&huart1, (uint8_t *)0x88, 1, HAL_MAX_DELAY);    // 发送接收完成信号
    }
}

/**
 * @brief 计算 base 的 exp 次幂
 * @param base 底数
 * @param exp 指数
 * @return 返回计算结果
 */
int Serial_Pow(int base, int exp)
{
    int result = 1;
    for (int i = 0; i < exp; i++)
    {
        result *= base;
    }
    return result;
}


uint8_t usart_state = 0;   // 接收状态。0: 等待数据，1: 等待第二个结束符，2: 等待第三个结束符
/**
 * @brief USART 接收完成回调函数
 * @param huart USART 句柄
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    int index = 0;
    if (huart->Instance == USART1)
    {
        switch (usart_state)
        {

        case 0:    // 等待数据
            if (Serial_ReceiveBuffer[Serial_ReceiveIndex] == 0xFF)    // 收到第一个结束符
            {
                usart_state = 1;
            }
            else
            {
                Serial_ReceiveIndex++;
            }
            HAL_UART_Receive_IT(huart, Serial_ReceiveBuffer + Serial_ReceiveIndex, 1);
            break;

        case 1:    // 等待第二个结束符
            if (Serial_ReceiveBuffer[Serial_ReceiveIndex] == 0xFF)    // 收到第二个结束符
            {
                usart_state = 2;
                HAL_UART_Receive_IT(huart, Serial_ReceiveBuffer + Serial_ReceiveIndex, 1);
            }
            else    // 数据包格式错误，丢弃
            {
                Serial_ReceiveIndex = 0;
                HAL_UART_Receive_IT(huart, Serial_ReceiveBuffer, 1);
            }
            break;

        case 2:    // 等待第三个结束符
            if (Serial_ReceiveBuffer[Serial_ReceiveIndex] == 0xFF)    // 收到第三个结束符
            {
                Serial_ReceiveBuffer[Serial_ReceiveIndex] = '\0';
                usart_state = 0;
                Serial_ReceiveReadyFlag = 1;
            }
            Serial_ReceiveIndex = 0;
            HAL_UART_Receive_IT(huart, Serial_ReceiveBuffer, 1);
            break;

        default:
            break;
        }
    }
}
