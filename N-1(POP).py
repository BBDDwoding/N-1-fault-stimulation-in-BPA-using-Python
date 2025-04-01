'''
    changes in desktop computer version：
    1. font in plt
    2. .dat, .bse and .swi file directory
    3. time.sleep()
      '''
import os
import time

import matplotlib.pyplot as plt
import pandas as pd

# 使用matplotliblib画图若中文或负号无法显示，可使用rcParams函数里的参数修改默认的属性
# 设置全局字体
plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = 'False'  # 正常显示负号


def is_zh(char):
    """判断是否汉字：使用Python内置的ord()函数将字符转换为Unicode编码，然后判断其范围是否在汉字的范围内："""
    if '\u4e00' <= char <= '\u9fff':
        return True
    else:
        return False


def is_not_zh(char):
    """ 判断是否西文字符，包含空格和标点符号 """
    return not is_zh(char)


def get_line_card(powerflow_file, L_card_file):
    """ read .dat files--存储潮流线路、节点等数据，为在.swi文件中修改故障做准备 """
    # 修改编码方式和错误处理机制--字符串中含有utf-8或gbk无法编码的字符情况
    dat = open(powerflow_file, 'r', encoding='gb18030', errors='ignore')
    dat_lines = dat.readlines()  # dtype=list,每个元素为一整行数据构成的字符串
    dat.close()

    L_card_list = []  # L卡集合，存储所有L卡信息
    dat_lines_n = 163  # L卡初始位置
    while dat_lines_n < len(dat_lines):
        card_typ = str(dat_lines[dat_lines_n])[0:2]  # 数据卡片类型，字符串格式
        if card_typ == 'L ':
            L_card_list.append(str(dat_lines[dat_lines_n]))
        dat_lines_n += 1
    L_card_series = pd.Series(L_card_list)
    L_card_series.to_csv(L_card_file, encoding='gb18030')
    return L_card_list


def fault_cfg(transient_file, L_card_list, L_card_list_n=0):
    """ overwrite .swi files (修改故障) """
    swi = open(transient_file, 'r')
    swi_lines = swi.readlines()  # 字符串类型

    ''' 注意:mode "w" 会先清空文件--备份文件防止写入失败;慎用其他模式，如'w+'----先了解用法  '''
    swi = open(transient_file, "w")
    # 以下是对不同特定位置进行检测，确认线路信息起始/终点位置
    bus1_col_st = 6 - is_zh(str(L_card_list[L_card_list_n])[3])
    bus1_col_end = bus1_col_st + 9 + is_not_zh(str(L_card_list[L_card_list_n])[bus1_col_st + 1]) + is_not_zh(
        str(L_card_list[L_card_list_n])[bus1_col_st + 2]) - is_zh(str(L_card_list[L_card_list_n])[bus1_col_st + 3])
    bus2_col_st = bus1_col_end + 1
    bus2_col_end = bus2_col_st + 9 + is_not_zh(str(L_card_list[L_card_list_n])[bus2_col_st + 1]) + is_not_zh(
        str(L_card_list[L_card_list_n])[bus2_col_st + 2]) - is_zh(str(L_card_list[L_card_list_n])[bus2_col_st + 3])
    bus1_info = str(L_card_list[L_card_list_n])[bus1_col_st:bus1_col_end]
    bus2_info = str(L_card_list[L_card_list_n])[bus2_col_st:bus2_col_end]
    branch_parallel_code = str(L_card_list[L_card_list_n])[bus2_col_end]
    fault_param_st = "   3   3.6         .6155"
    fault_param_end = "   3   8.6         .6155"
    fault_start_info = "LS  " + bus1_info + "  " + bus2_info + " " + branch_parallel_code + fault_param_st + "\n"
    fault_end_info = "LS  " + bus1_info + "  " + bus2_info + " " + branch_parallel_code + fault_param_end + "\n"
    swi_lines[18] = fault_start_info  # 故障开始卡需填信息
    swi_lines[19] = fault_end_info  # 故障结束卡需填信息
    for _ in swi_lines:
        swi.write(_)
    swi.close()


def bpa_call(swnt, bse_file, transient_file, sleeptime=11):
    ''' run .swi file '''
    os.system("start" + " " + swnt + " " + bse_file + " " + transient_file)  # calling bpa execute .swi file
    time.sleep(sleeptime)
    ''' 注意:时间太短会导致swx文件结果未全部写完---------计时/缩短仿真时间？ '''


def get_output(swx_file, L_card_list_n):
    """ read data from 监视曲线数据列表 """
    swx = open(swx_file, 'r')
    output_info = swx.readlines()
    swx.close()

    cycle = []
    power_angle = []
    vol_high = []
    gap = 4
    i = output_info.index(' * 计算过程中的监视曲线数据列表\n') + gap  # index():字符串查找---better way?
    output_list_len = 600  # 440504-441108
    cycle_col_st = 3 - 2  # 对应notepad++中显示的第3行
    cycle_col_end = 8 - 1  # 对应notepad++中显示的第8行
    power_angle_col_st = 40 - 2  # 对应notepad++中显示的第40行
    power_angle_col_end = 46 - 1  # 对应notepad++中显示的第46行
    vol_high_col_st = 64 - 2
    vol_high_col_end = 70 - 1
    while i < output_info.index(' * 计算过程中的监视曲线数据列表\n') + gap + output_list_len:
        cycle.append(float(output_info[i][cycle_col_st:cycle_col_end]))
        power_angle.append(float(output_info[i][power_angle_col_st:power_angle_col_end]))
        vol_high.append(float(output_info[i][vol_high_col_st:vol_high_col_end]))
        i += 1
    df = pd.DataFrame({"cycle": cycle, "power_angle": power_angle, "vol_high": vol_high})
    df.to_csv(f'D:\\study\\WAMS科技项目\\机电数据\\仿真结果\\sim{L_card_list_n}.csv', encoding='gb18030')
    plt.plot(cycle, power_angle, label='功角')
    # plt.plot(cycle, vol_high, label = '电压')


def plot_curves(x_label=None, y_label=None, title_info=None, grid_on=True):
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title_info)
    plt.legend(loc='best')
    plt.grid(grid_on)
    plt.show()


if __name__ == '__main__':
    # paths setting
    swnt = "D:\\PSD\\PSDEditCEPRI\\swnt.exe"
    powerflow_file = "D:\\study\\WAMS科技项目\\机电数据\\HD-2025XD.dat"
    transient_file = "D:\\study\\WAMS科技项目\\机电数据\\HD-2025XD.swi"
    bse_file = "D:\\study\\WAMS科技项目\\机电数据\\HD-2025XD.BSE"
    swx_file = "D:\\study\\WAMS科技项目\\机电数据\\HD-2025XD.SWX"
    L_card_file = 'D:\\study\\WAMS科技项目\\机电数据\\仿真结果\\L_card_series.csv'
    # sim_res_file = 

    L_card_list = get_line_card(powerflow_file, L_card_file)
    L_card_list_n = 450
    step = 500
    while L_card_list_n < len(L_card_list):
        print(L_card_list_n)
        fault_cfg(transient_file, L_card_list, L_card_list_n)
        bpa_call(swnt, bse_file, transient_file)
        get_output(swx_file, L_card_list_n)
        L_card_list_n += step
    plot_curves(x_label='TIME (S)', y_label='发电机最大相对功角(°)', title_info='监视曲线', grid_on=True)
