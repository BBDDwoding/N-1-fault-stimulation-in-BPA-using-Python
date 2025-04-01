"""
    changes in desktop computer version：
    2. file  path
    3. time.sleep()
      """
# TODO:
#  1.vscode using skills; origin; github
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 使用matplotlib画图若中文或负号无法显示，可使用rcParams函数里的参数修改默认的属性
# 设置全局字体
plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = 'False'  # 正常显示负号


def is_zh(char):
    """
    判断是否汉字：使用Python内置的ord()函数将字符转换为Unicode编码，然后判断其范围是否在汉字的范围内
    """
    if '\u4e00' <= char <= '\u9fff':
        return True
    else:
        return False


def is_not_zh(char):
    """
    判断是否西文字符，包含空格和标点符号
    """
    return not is_zh(char)


def word_search(file, words, unwanted=None):
    """
    搜索指定词汇，返回其在文本中每次出现的位置

    :param file: target file
    :param words: target words
    :param unwanted: unwanted words in the same row with target words
                    (used to remove interference)
    :return: list containing indices target words occurred in the file
    """
    if unwanted is None:
        unwanted = []
    row_no = 0  # 文本行数起始位置
    word_indices = []  # 指定词汇在文本中出现的具体行数列表

    with open(file, 'r') as f:
        for index, line in enumerate(f):
            """ 通过unwanted词汇，排除干扰行 """
            is_unwanted = False
            for _ in unwanted:
                is_unwanted = is_unwanted or (_ in line)  # 出现unwanted词汇即排除
            if (words in line) and (not is_unwanted):
                word_indices.append(index)  # 找到词汇且无unwanted词汇即添加
            row_no += 1

    print("文本总行数:%s" % row_no)
    print(f"{words}在文本中出现的次数为：{len(word_indices)}次，"
          f"具体行数为：{word_indices}")
    return word_indices


class BPA:
    """
    Predecessor of class Dat and class Swi, receive file path as attributes,
    including method to simulate
    """

    def __init__(self, file):
        self.file = file  # .dat/.swi file path

    def simulate(self, exe, bse_file=None):
        """
        call bpa to simulate .dat/.swi file

        :param bse_file:
        :param exe: pfnt/swnt.exe path
        """
        sep = ' '
        seq = ['start', exe]
        if bse_file is not None:
            seq.append(bse_file)
        seq.append(self.file)
        command = sep.join(seq)
        os.system(command)
        # 等价于 os.system("start" + " " + swnt + " " + bse_file + " " + transient_file)
        time.sleep(11.5)  # TODO:use subprocess() to judge if thread is done??


class Dat(BPA):
    def __init__(self, file):
        super().__init__(file)  # :param file: .dat file path

    def get_eqp_cards(self, eqp_cards_file, eqp_card):
        """
        :param eqp_card: equipment card card_type
        :param eqp_cards_file: 输出csv文件路径，存储所有设备卡信息
        :return: 存储所有设备卡信息列表
        """
        # 修改编码方式和错误处理机制--字符串中含有utf-8或gbk无法编码的字符情况
        with open(self.file, 'r', encoding='gb18030', errors='ignore') as dat:
            dat_rows = dat.readlines()  # dtype=list,每个元素为一整行数据构成的字符串

        eqp_cards_lst = []  # 设备卡集合，存储所有设备卡信息
        for dat_rows_no in range(0, len(dat_rows)):
            if str(dat_rows[dat_rows_no]).startswith(eqp_card):
                eqp_cards_lst.append(str(dat_rows[dat_rows_no]))

        pd.Series(eqp_cards_lst).to_csv(eqp_cards_file, encoding='gb18030')  # 输出csv文件存储所有设备卡信息
        return eqp_cards_lst


class Swi(BPA):
    def __init__(self, file):
        super().__init__(file)  # :param file: .swi file path

    def fault_cfg(self, l_cards_lst, l_cards_lst_no=0):
        """
        overwrite .swi file(修改故障)

        :param l_cards_lst: 存储所有L卡信息列表
        :param l_cards_lst_no: 目前读取的L卡在列表中的索引
        :return: None
        """
        swi = open(self.file, 'r')
        swi_rows = swi.readlines()

        ''' 注意:mode "w" 会先清空文件--备份文件防止写入失败 '''
        swi = open(self.file, "w")
        # print(cards_lst_no)      # 检测线路出错位置
        # TODO:special check for wechat screenshot‘s position
        l_card_info = str(l_cards_lst[l_cards_lst_no])

        # 以下是对不同特定位置进行检测，确认线路信息起始/终点位置
        bus1_col_st = 6 - is_zh(l_card_info[3])
        bus1_col_end = bus1_col_st + 9 + is_not_zh(l_card_info[bus1_col_st + 1]) + is_not_zh(
            l_card_info[bus1_col_st + 2]) - is_zh(l_card_info[bus1_col_st + 3])
        bus2_col_st = bus1_col_end + 1
        bus2_col_end = bus2_col_st + 9 + is_not_zh(l_card_info[bus2_col_st + 1]) + is_not_zh(
            l_card_info[bus2_col_st + 2]) - is_zh(l_card_info[bus2_col_st + 3])
        bus1_info = l_card_info[bus1_col_st:bus1_col_end]
        bus2_info = l_card_info[bus2_col_st:bus2_col_end]
        branch_parallel_code = l_card_info[bus2_col_end]

        fault_param_st = "   3   3.6         .6155"
        fault_param_end = "   -3   299         .6155"
        fault_start_info = "LS  " + bus1_info + "  " + bus2_info + " " + branch_parallel_code + fault_param_st + "\n"
        fault_end_info = "LS  " + bus1_info + "  " + bus2_info + " " + branch_parallel_code + fault_param_end + "\n"
        swi_rows[18] = fault_start_info  # 故障开始卡需填信息
        swi_rows[19] = fault_end_info  # 故障结束卡需填信息
        for _ in swi_rows:
            swi.write(_)
        swi.close()


class Equipment:
    """
    Equipment information in .SWX file, predecessor of all equipment card_type
    in the output list
    """
    read_span = 600

    def __init__(self, swx_file, type, eqps_indices):
        """
        :param swx_file: .swx file path
        :param type: equipment card_type
        :param eqps_indices: equipments indices in .swx file
        """
        self.type = type
        self.eqps_indices = eqps_indices
        with open(swx_file, encoding='gb18030') as swx:
            self.swx_info = swx.readlines()
        self.fieldnames = self.swx_info[self.eqps_indices[0] + 2].split()  # 2为查找到的标题所含关键词所在行数与字段开始行数间隔

    def reader(self, l_cards_lst_no, csvdir):
        """
        read equipment data

        :param l_cards_lst_no: index of l_card currently being read
        :param csvdir: output file(csv) directory
        :output: .csv file containing simulation result
        """
        for eqp_no in range(len(self.eqps_indices)):
            # enumerate every equipment
            eqp_index = self.eqps_indices[eqp_no]
            if '\"' in self.swx_info[eqp_index]:
                eqp_name = self.swx_info[eqp_index].split('\"')[1]
            else:
                eqp_name = ''  # specify for monitor
            field_data = [[] for _ in self.fieldnames]
            for i in range(self.read_span):
                field_info = self.swx_info[eqp_index + 4 + i].split()  # title_data_gap=4
                for _ in range(len(self.fieldnames)):
                    if self.type == 'MON' and _ != 0:
                        field_data[_].append(field_info[3 * _ + 2])
                    else:
                        field_data[_].append(field_info[_])
            df = pd.DataFrame(np.array(field_data).T, columns=self.fieldnames)
            df.to_csv(os.path.join(csvdir, f'sim{l_cards_lst_no}{self.type}{eqp_name}.csv'),
                      encoding='gb18030')  # necessary with data containing zh

    def plot_curves(self, folder, step=1):
        """
        根据输出数据绘图

        :param folder: where target files are
        :param step: 可改变步长来改变绘制曲线条数
        """
        file_lst = os.listdir(folder)
        for field_name in self.fieldnames:  # enumerate every equipment field_data
            if field_name != '时间':
                for file_no in range(0, len(file_lst), step):  # enumerate every file in the folder
                    filename = file_lst[file_no]
                    if self.type in filename and filename.startswith('sim') \
                            and filename.endswith('.csv'):  # check filename
                        file_path = os.path.join(folder, filename)  # generate full path
                        df = pd.read_csv(file_path, encoding='gb18030')  # read data
                        field_data = df.loc[:, field_name]
                        plt.plot(df.iloc[:, 0], field_data)
                plt.xlabel('时间')
                plt.ylabel(field_name)
                plt.title('Simulation result')
                plt.legend(loc='best')
                plt.grid(True)
                plt.show()


class Generator(Equipment):
    def __init__(self, swx_file):
        super().__init__(swx_file, type='GEN',
                         eqps_indices=word_search(swx_file, words='参考机'))


class Bus(Equipment):
    def __init__(self, swx_file):
        super().__init__(swx_file, type='BUS',
                         eqps_indices=word_search
                         (swx_file, unwanted=['直流', '最高', 'WARNING'], words='节点'))


class Line(Equipment):
    def __init__(self, swx_file):
        super().__init__(swx_file, type='LINE',
                         eqps_indices=word_search(swx_file, words='线路'))


class Monitor(Equipment):
    def __init__(self, swx_file):
        super().__init__(swx_file, type='MON',
                         eqps_indices=word_search(swx_file, words='监视'))


if __name__ == '__main__':
    swnt = r"D:\PSD\PSDEditCEPRI\swnt.exe"
    projectdir = 'D:/study/WAMS科技项目/机电数据'
    csvdir = os.path.join(projectdir, '仿真结果')
    powerflow_file = os.path.join(projectdir, 'HD-2025XD.dat')
    transient_file = os.path.join(projectdir, 'HD-2025XD.swi')
    bse_file = os.path.join(projectdir, 'HD-2025XD.BSE')
    swx_file = os.path.join(projectdir, 'HD-2025XD.SWX')
    eqp_cards_file = os.path.join(csvdir, 'l_cards_series.csv')

    dat = Dat(powerflow_file)
    l_cards_lst = dat.get_eqp_cards(eqp_cards_file, eqp_card='L ')  # 从dat文件中获取所有L卡信息
    ''' wanna plot only: add the equipment in the next line and comment the <for loop> out.
        notice: .swx file CANNOT be empty'''
    equipments = [Monitor(swx_file)]
    for l_cards_lst_no in range(0, len(l_cards_lst), 50):
        # 对每一条L卡所含线路进行N-1故障模拟，存储结果
        swi = Swi(transient_file)
        swi.fault_cfg(l_cards_lst, l_cards_lst_no)
        swi.simulate(swnt, bse_file)
        equipments = [Monitor(swx_file)]
        for equipment in equipments:
            equipment.reader(l_cards_lst_no, csvdir)
    for equipment in equipments:
        """ if plotting the wrong figure,delete the original files and get data again """
        equipment.plot_curves(csvdir)
