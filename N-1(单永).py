"""
    changes in desktop computer version：
    2. file  path
    3. time.sleep()
      """
# TODO:
#  1.vscode using skills; origin; github; AI aided coding
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


def word_search(file, query, noise=None):
    """
    搜索指定词汇，返回其在文本中每次出现的位置

    :param file: target file
    :param query: target words
    :param noise: noisy words in the same row with target words
                    (used to remove interference)
    :return: list containing indices target words occurred in the file
    """
    if noise is None:
        noise = []
    row_no = 0  # 文本行数起始位置
    key_indices = []  # 指定词汇在文本中出现的具体行数列表

    with open(file, encoding='gb18030') as f:
        for index, line in enumerate(f):
            """ 通过noisy词汇，排除干扰行 """
            is_noise = False
            for _ in noise:
                is_noise = is_noise or (_ in line)  # 出现noise词汇即排除
            if (query in line) and (not is_noise):
                key_indices.append(index)  # 找到词汇且无noise词汇即添加
            row_no += 1

    print("文本总行数:%s" % row_no)
    print(f"{query}在文本中出现的次数为：{len(key_indices)}次，"
          f"具体行数为：{key_indices}")
    return key_indices


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
        time.sleep(19)  # TODO:use subprocess() to judge if thread is done??


class Dat(BPA):
    def __init__(self, file):
        super().__init__(file)  # :param file: .dat file path

    def get_cards(self, cards_file, card_type):
        """
        :param card_type: card type
        :param cards_file: 输出csv文件路径，存储所有卡信息
        :return: 存储所有卡信息列表
        """
        # 修改编码方式和错误处理机制--字符串中含有utf-8或gbk无法编码的字符情况
        with open(self.file, 'r', encoding='gb18030', errors='ignore') as file:
            cards_rows = file.readlines()  # dtype=list,每个元素为一整行数据构成的字符串

        cards_lst = []  # 卡集合，存储所有卡信息
        for cards_rows_no in range(0, len(cards_rows)):
            if str(cards_rows[cards_rows_no]).startswith(card_type):
                cards_lst.append(str(cards_rows[cards_rows_no]))

        pd.Series(cards_lst).to_csv(cards_file, encoding='gb18030')  # 输出csv文件存储所有卡信息
        return cards_lst


class Swi(BPA):
    def __init__(self, file):
        super().__init__(file)  # :param file: .swi file path

    def fault_config(self, cards_lst, cards_lst_no=0):
        """
        overwrite .swi file(修改故障)

        :param cards_lst: 存储所有L卡信息列表
        :param cards_lst_no: 目前读取的L卡在列表中的索引
        :return: None
        """
        swi = open(self.file, 'r')
        swi_rows = swi.readlines()

        ''' 注意:mode "w" 会先清空文件--备份文件防止写入失败 '''
        swi = open(self.file, "w")
        print(cards_lst_no)
        # TODO:special check for wechat screenshot‘s position
        card_info = cards_lst[cards_lst_no]
        split_card_info = card_info.split()
        is_owner = len(split_card_info[1]) <= 3  # check if there is a (zh)owner
        if is_not_zh(split_card_info[1 + is_owner][0]):  # owner links with bus info:'H苏----‘
            split_card_info[1 + is_owner] = split_card_info[1 + is_owner][1:]
        if len(split_card_info[1 + is_owner]) <= 8:  # flt bus1 has a space between bus name and base voltage
            flt_bus1 = split_card_info[1 + is_owner] + split_card_info[2 + is_owner] + '.'
            if len(split_card_info[3 + is_owner]) <= 8:  # flt bus2 has a space between bus name and base voltage
                flt_bus2 = split_card_info[3 + is_owner] + split_card_info[4 + (
                    is_owner)][:-1] + '.' + split_card_info[4 + is_owner][-1]
            else:
                flt_bus2 = split_card_info[2 + is_owner]
        else:  # flt bus1 without a space between bus name and base voltage
            flt_bus1 = split_card_info[1 + is_owner]
            if len(split_card_info[2 + is_owner]) <= 8:  # flt bus2 has a space between bus name and base voltage
                flt_bus2 = split_card_info[2 + is_owner] + split_card_info[3 + is_owner][:-1] \
                           + '.' + split_card_info[3 + is_owner][-1]
            else:  # both base voltage with .
                flt_bus2 = split_card_info[2 + is_owner]

        flt_args = ' 3 1 1 5.004.505.00            25.025.030.030.0\n'
        if len(flt_bus2) <= 9:  # without circuit number
            flt_args = ' ' + flt_args

        swi_rows[18] = ' '.join(
            ['FLT', flt_bus1, flt_bus2, flt_args])  # 故障开始卡需填信息
        print(swi_rows[18])

        for _ in swi_rows:
            swi.write(_)
        swi.close()


class Equipment:
    """
    Equipment information in .SWX file, predecessor of all equipment types
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
                eqp_name = ''  # specify for monitoring curves
            field_data = [[] for _ in self.fieldnames]
            for i in range(self.read_span):
                field_info = self.swx_info[eqp_index + 4 + i].split()  # title-data's gap=4
                for _ in field_info:
                    if len(_) == 11:
                        part1 = _[:5]
                        part2 = _[-6:]
                        index = field_info.index(_)
                        field_info[index] = part1
                        field_info.insert(index + 1, part2)
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
                        df = pd.read_csv(file_path, encoding='gb18030', index_col=0)  # read data
                        field_data = df.loc[:, field_name]
                        print_flag = 0
                        for _ in field_data:
                            if _ > 300 and print_flag == 0:  # check for unstable cases
                                print(filename)
                                print_flag = 1
                        plt.plot(df.iloc[:, 0] * 0.02, field_data)
                plt.xlabel('时间')
                plt.ylabel(field_name)
                plt.title('Simulation result')
                plt.legend(loc='best')
                plt.grid(True)
                plt.show()


class Generator(Equipment):
    """
    输出设备类型：发电机
    """

    def __init__(self, swx_file):
        super().__init__(swx_file, type='GEN',
                         eqps_indices=word_search(swx_file, query='参考机'))


class Bus(Equipment):
    """
    输出设备类型：节点/母线
    """

    def __init__(self, swx_file):
        super().__init__(swx_file, type='BUS',
                         eqps_indices=word_search
                         (swx_file, noise=['直流', '最高', 'WARNING'], query='节点'))


class Line(Equipment):
    """
    输出设备类型：线路
    """

    def __init__(self, swx_file):
        super().__init__(swx_file, type='LINE',
                         eqps_indices=word_search(swx_file, query='线路'))


class Monitor(Equipment):
    """
    输出设备类型：监视曲线
    """

    def __init__(self, swx_file):
        super().__init__(swx_file, type='MON',
                         eqps_indices=word_search(swx_file, query='监视'))


if __name__ == '__main__':
    swnt = r"D:\PSD\PSDEditCEPRI\swnt.exe"
    projectdir = 'D:/study/WAMS科技项目/机电数据'
    csvdir = os.path.join(projectdir, '仿真结果cycle=300')
    powerflow_file = os.path.join(projectdir, 'HD-2025XD.dat')
    transient_file = os.path.join(projectdir, 'HD-2025XD.swi')
    bse_file = os.path.join(projectdir, 'HD-2025XD.BSE')
    swx_file = os.path.join(projectdir, 'HD-2025XD.SWX')
    # flt_file = r'D:\study\WAMS科技项目\LCC\data\single_phase\故障集.flt'
    # flt_cards_file = os.path.join(csvdir, 'flt_cards_series.csv')
    l_cards_file = os.path.join(csvdir, 'l_cards_series.csv')

    dat = Dat(powerflow_file)
    l_cards_lst = dat.get_cards(l_cards_file, card_type='L ')  # 从dat文件中获取所有L卡信息
    for l_cards_lst_no in range(187, len(l_cards_lst)):
        # 对每一条L卡所含线路进行N-1故障模拟，存储结果
        swi = Swi(transient_file)
        try:
            swi.fault_config(l_cards_lst, l_cards_lst_no)
            swi.simulate(swnt, bse_file)
            equipments = [Monitor(swx_file)]
            for equipment in equipments:
                equipment.reader(l_cards_lst_no, csvdir)
        except:
            print(f'the question lies on :{l_cards_lst_no}')  # 检测线路出错位置
            continue
    ''' plot only: comment out the simulation <for loop> above and add the equipment in the next line.
        notice: .swx file CANNOT be empty'''
    equipments = [Monitor(swx_file)]
    for equipment in equipments:
        """ In case of anomalous figures,delete the output files and simulate again """
        equipment.plot_curves(csvdir)
