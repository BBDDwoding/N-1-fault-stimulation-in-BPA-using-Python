import os
from collections import defaultdict

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = 'False'  # 正常显示负号


def load_data(file_dir, feature, step=1):
    """
    读取仿真数据

    :param file_dir: root directory where target files are
    :param step: 可改变步长来改变绘制曲线条数
    :return: Dataframe
    """
    file_list = os.listdir(file_dir)
    df = pd.DataFrame([], columns=[])
    for idx in range(0, len(file_list), step):  # enumerate every file in the folder
        file_name = file_list[idx]
        if file_name.endswith('.csv'):  # check filename
            file_path = os.path.join(file_dir, file_name)  # generate full path
            # read data
            feature_data = pd.read_csv(file_path, encoding='gb18030').loc[:1000, feature]
            df[file_name[:-7]] = feature_data
    return df


df_list = []
data_concat = pd.DataFrame([], columns=[])
features = ['最大发电机相对功角', '最低母线电压', '最大发电机频率', '最高母线电压', '最小发电机频率']
file_dir = r'D:\study\WAMS科技项目\Cluster\dsp仿真结果'

# data procession
for _ in range(len(features)):
    df_list.append(load_data(file_dir=file_dir, feature=features[_]))
    data_concat = pd.concat([data_concat, df_list[_]], axis=0, ignore_index=True)
print(data_concat)

data_processed = data_concat.T
data_processed.to_csv(os.path.join(file_dir, 'data_processed.csv'), index=False)
data_processed.info()
print(data_processed.values)

# KMeans clustering
n_cluster = 6
model = KMeans(n_clusters=n_cluster, max_iter=1000)
model.fit(data_processed.values)

mapping = defaultdict(list)
for i, label in enumerate(model.labels_):
    mapping[label].append(i)

# visualize
n_col = 1
n_row = len(features)

for label in mapping.keys():
    fig, axes = plt.subplots(nrows=n_row, ncols=n_col)

    for idx in mapping[label]:
        for feat_no in range(len(features)):
            df1 = data_processed.iloc[idx, feat_no * len(df_list[feat_no]):(feat_no + 1) * len(df_list[feat_no])].values
            axes[feat_no].plot(np.arange(len(df_list[feat_no])) * 0.02 * len(mapping[label]),
                               data_processed.iloc[idx,
                               feat_no * len(df_list[feat_no]):(feat_no + 1) * len(df_list[feat_no])].values)
            axes[feat_no].set_xlabel('时间(s)')
            axes[feat_no].set_ylabel(features[feat_no])
            axes[feat_no].set_title(f'{features[feat_no]}聚类 - 类别 {label + 1}')
    plt.tight_layout()
    plt.show()
