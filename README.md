# N-1-fault-simulations-with-BPA-and-clustering-using-Python
# (Python调用BPA实现批量N-1故障仿真和结果提取+自动聚类)
Use Python to:
1. configure and run N-1 fault simulations with BPA
2. extract results from .swx files and store in .csv files
3. clustering with KMeans
熟悉Python调用BPA的相关API，通过Python实现潮流计算和机电暂态稳定仿真。
编写python代码，实现N-1故障扰动下，BPA仿真结果自动提取，包括：暂态电压、线路暂态功率、发电机功角等，将上述数据形成样本库。
熟悉聚类方法代码，将上述不同类型暂态数据分类。

Contents：
1. batch-simulation.zip(version 0): the original version of code using sequential structure with plotted curves
2. N-1(POP).py(version 1): Process Oriented Programming Version, wrap utilities into the form of functions
3. N-1(OOP).py(version 2): Object Oriented Programming Version
4. N-1(单永).py(latest version): update the fault-config part
5. cluster.py：modified from Jiangsu two-staged clustering .ipynb
