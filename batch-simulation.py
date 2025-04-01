import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# 使用matplotliblib画图若中文或负号无法显示，可使用rcParams函数里的参数修改默认的属性
# 设置全局字体
plt.rcParams['font.family'] = 'Arial Unicode MS' 
plt.rcParams['axes.unicode_minus'] = 'False' # 正常显示负号

swnt = "D:\\PSD\\PSDEditCEPRI\\swnt.exe"    # program for .swi file  
powerflow_file = "D:\\study\\WAMS科技项目\\LCC\\result\\直流落点往交流5步以内路线_去重.dat"
transient_file = "D:\\study\\WAMS科技项目\\机电数据\\HD-2025XD.swi"         # .swi file path

# read .dat files--存储潮流线路、节点等数据，为在.swi文件中修改故障做准备
# 修改编码方式和错误处理机制--字符串中含有utf-8或gbk无法编码的字符情况
dat = open(powerflow_file, 'r', encoding='gb18030', errors='ignore')   
dat_lines = dat.readlines()  # 字符串类型
dat.close()

dat_lines_n=0     # L卡初始位置
while dat_lines_n<41:
    # print(dat_lines[dat_lines_n:dat_lines_n+1][0])    # 线路卡信息
    # print(str(dat_lines[dat_lines_n])[6:26])  # 待移植到故障卡的信息

    # 测试读写数据正确性
    swi = open(transient_file, 'r')
    swi_lines = swi.readlines()  # 字符串类型
    # print(swi_lines[18:20])   # 故障卡信息
    # print(list(swi_lines[18])[4:26])  # 故障开始卡需填信息
    # print(list(swi_lines[19])[4:26])  # 故障结束卡需填信息

    # overwrite .swi files (修改故障)
    ''' 注意:mode "w" 会先清空文件--备份文件防止写入失败;慎用其他模式，如'w+'----先了解用法  '''
    swi = open(transient_file, "w")     
    swi_lines[18] = "LS  " + str(dat_lines[dat_lines_n])[6:15]+ "  " + str(dat_lines[dat_lines_n])[16:25] + " " + str(dat_lines[dat_lines_n])[25] + "   3   3.6         .6155" + "\n"
    swi_lines[19] = "LS  " + str(dat_lines[dat_lines_n+1])[6:15]+ "  " + str(dat_lines[dat_lines_n+1])[16:25] + " " + str(dat_lines[dat_lines_n+1])[25] + "   3   8.6         .6155" + "\n"
    for _ in swi_lines:
        swi.write(_)
    swi.close()

    # 测试读写数据正确性
    # swi = open(transient_file, 'r')
    # swi_lines = swi.readlines()  # 字符串类型
    # print(swi_lines[18:20])   # 故障卡信息
    # print(list(swi_lines[18])[4:26])  # 故障开始卡需填信息
    # print(list(swi_lines[19])[4:26])  # 故障结束卡需填信息
       
    # run .swi file
    os.system("start" + " " + swnt + " " + "D:\\study\\WAMS科技项目\\机电数据\\HD-2025XD.BSE" + " " + transient_file)   #calling bpa execute .swi file
    time.sleep(43) 
    ''' 注意:时间太短会导致swx文件结果未全部写完---------计时/缩短仿真时间？ '''

    #read data from 监视曲线数据列表
    swx = open("D:\\study\\WAMS科技项目\\机电数据\\HD-2025XD.SWX", 'r')
    output_info = swx.readlines()
    swx.close()
    print(len(output_info))     # 获取目前已经输出的swx文件长度
    # print(output_info[440500])
    # print(output_info.index(' * 计算过程中的监视曲线数据列表\n'))

    cycle = []
    power_angle = []
    gap = 4   
    i = output_info.index(' * 计算过程中的监视曲线数据列表\n') + gap    # index():字符串查找---better way?
    output_list_length = 300
    cycle_column_start = 3-2
    cycle_column_end = 8-1
    power_angle_column_start = 40-2
    power_angle_column_end = 46-1
    while i < output_info.index(' * 计算过程中的监视曲线数据列表\n')+ gap + output_list_length:     
        cycle.append(float(output_info[i][cycle_column_start:cycle_column_end]))    # 对应notepad++中显示的3-8行
        power_angle.append(float(output_info[i][power_angle_column_start:power_angle_column_end]))    # 对应notepad++中显示的40-46行
        i += 1

    plt.plot(cycle, power_angle)
    dat_lines_n += 1

plt.xlabel('TIME (S)')
plt.ylabel('功角差(°)')
plt.title('监视曲线')
plt.legend(loc='best')
plt.grid(True)  
plt.show()
