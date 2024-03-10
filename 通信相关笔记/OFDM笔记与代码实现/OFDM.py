

import numpy as np

# region 参数定义
number_of_subcarriers = 52 # 子载波数，不包含直流
number_of_FFT = 64 # FFT长度64
number_of_cyclic_prefix = 16 # 循环前缀长度
number_of_symbo = number_of_FFT + number_of_cyclic_prefix # 符号长度
number_of_carriers = 53 # 包含直流的载波数量

number_of_phase = 4 # 4相位调制

SNR = np.arange(0,25,1)# 不同的仿真 信噪比
number_of_frame = 10 # 每种信噪比下面的仿真 帧数
number_of_symbo_pre_frame = 6 # 每一帧下面的OFDM符号数

P_f_inter = 6 # 导频间隔
# 导频位置

convolutional_code_length = 7 # 卷积码约束长度
# viterbi译码器回溯深度
# m序列的阶数
# m序列的寄存器链接方式
# m序列的寄存器初始值

# endregion


# region 基带数据
baseband_datas = np.random.randint(0, 2, size=(1, number_of_subcarriers * number_of_frame * number_of_symbo_pre_frame))
# print(baseband_datas)
# endregion

# region 信道编码

# endregion
