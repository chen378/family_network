import pickle

import pandas as pd
from config import ROOT
import os
import networkx as nx
import pandas as pd
import numpy as np

# 读取 collect.json文件
def collect_read(file_path,node_delay_csv,Ff=True, Sf=True, Tf=True):
    """
    读取生成collect表单的统计信息，统计节点出现频次
    """
    # 读取 CSV 文件
    # 以ip为主键
    # df = pd.read_csv(file_path)
    # # 获取 ip_str 列
    # ip_str_column = df['ip_str']
    # # 存储所有 IP 地址的列表
    # all_ips = []
    #
    # for entry in ip_str_column:
    #     ips = entry.split(' ')
    #     all_ips.extend(ips)
    #
    # ip_counts = {}
    # for ip in all_ips:
    #     if ip in ip_counts:
    #         ip_counts[ip] += 1
    #     else:
    #         ip_counts[ip] = 1
    #
    # frequent_ips = {}
    # for ip, count in ip_counts.items():
    #     if count > 7:
    #         frequent_ips[ip] = count
    # return frequent_ips

    # 以fingerprint（path_str）为主键 目前平均值为delay:0.308962626	variance:0.017804916 times:13.16234355 bandwidth:15311
    df = pd.read_csv(file_path)
    # 将 path_str 拆分为多个列
    df[['fp1', 'fp2', 'fp3']] = df['path_str'].str.split(expand=True)
    # 融合拆分的列
    melted_df = pd.melt(df, id_vars=['delay', 'variance', 'time'], value_vars=['fp1', 'fp2', 'fp3'], value_name='fingerprint')
    # 移除 NaN 值
    melted_df = melted_df.dropna(subset=['fingerprint'])
    # 聚合操作
    result_df = melted_df.groupby('fingerprint').agg(
        delay=('delay', 'mean'),
        variance=('variance', 'mean'),
        times=('fingerprint', 'count')
    ).reset_index()
    result_df.to_csv(node_delay_csv, index=False)

def clean_day2node(input_file, output_file):
    """
    处理 day.csv 文件，以 finger 为主键，对指定列进行映射，保留第一次出现的值，
    对 bandwidth 做均值聚合，并记录 bandwidth 的出现次数，以 bandwidth_change_times 存储。

    :param input_file: 输入的 day.csv 文件路径
    :param output_file: 输出的 node.csv 文件路径
    """
    # 读取 day.csv 文件
    df = pd.read_csv(input_file)

    # 定义需要保留第一次出现值的列
    columns_to_keep_first = [
        'nickname', 'ip', 'dirport', 'Authority', 'BadExit', 'Exit',
        'Fast', 'Guard', 'Stable', 'V2Dir', 'HSDir', 'version'
    ]

    # 以 finger 为主键，对指定列进行分组
    grouped = df.groupby('finger')

    # 对需要保留第一次出现值的列，取第一个值
    first_values = grouped[columns_to_keep_first].first()

    # 计算 bandwidth 的均值
    bandwidth_mean = grouped['bandwidth'].mean()

    # 计算 bandwidth 的出现次数
    bandwidth_change_times = grouped['bandwidth'].count()

    # 合并结果
    result = pd.concat([first_values, bandwidth_mean, bandwidth_change_times], axis=1)
    result = result.rename(columns={'bandwidth': 'bandwidth_mean', 'bandwidth': 'bandwidth_change_times'})

    # 保存结果到 node.csv 文件
    result.to_csv(output_file, index=True)



def clean_delay2node(input_file, output_file):
    """
    以输入的 fringerprint 为主键，从输入文件中获取 delay、variance 和 times 列，
    将 fringerprint 列名改为 finger 后，写入输出文件。
    已去重的数据无需额外处理，若输出 CSV 中无对应值则填充为 0。

    :param input_file: 输入的 node_delay.csv 文件路径
    :param output_file: 输出的 node.csv 文件路径
    """
    try:
        # 读取输入文件
        df = pd.read_csv(input_file)

        # 检查输入文件中是否存在 fringerprint 列
        if 'fingerprint' not in df.columns:
            raise KeyError("输入文件中未找到 'fingerprint' 列，请检查输入文件内容。")

        # 选择需要的列
        selected_columns = ['fingerprint', 'delay', 'variance', 'times']
        df_selected = df[selected_columns]

        # 将 fringerprint 列名改为 finger
        df_selected.rename(columns={'fingerprint': 'finger'}, inplace=True)

        # 检查输出文件是否存在
        if os.path.exists(output_file):
            # 读取原有输出文件
            df_output = pd.read_csv(output_file)

            # 合并数据
            merged_df = pd.merge(df_output, df_selected, on='finger', how='left')

            # 填充缺失值为 0
            merged_df.fillna(0, inplace=True)

            # 将合并后的数据写入输出文件
            merged_df.to_csv(output_file, index=False)
        else:
            # 如果输出文件不存在，直接写入新数据
            df_selected.to_csv(output_file, index=False)

        print(f"数据已成功写入 {output_file}")
    except FileNotFoundError:
        print(f"输入文件 {input_file} 未找到，请检查文件路径。")
    except KeyError as ke:
        print(f"列名错误: {ke}")
    except Exception as e:
        print(f"处理过程中出现错误: {e}")

# 定义非线性归一化函数（这里使用sigmoid函数）
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def normalize(value, avg, max_val, min_val):
    # 首先进行线性归一化
    norm_value = (value - min_val) / (max_val - min_val)
    # 然后使用sigmoid函数进行非线性归一化
    return sigmoid(norm_value) * 2 - 1  # 映射到 -1 到 1 之间

def build_graph_from_csv(csv_file):
    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 提取所需的列
    path_strs = df['path_str']
    delays = df['delay']
    variances = df['variance']

    # 定义归一化所需的参数
    delay_avg = 0.307690167
    delay_max = 3.2631582
    delay_min = 0.0283798
    variance_avg = 0.016208862
    variance_max = 8.139860049
    variance_min = 0

    # 创建一个空的无向图
    G = nx.Graph()

    # 遍历每一行数据
    for path_str, delay, variance in zip(path_strs, delays, variances):
        # 分割path_str
        paths = path_str.split(' ')  # 假设path_str是由3个空格隔开的

        # 计算归一化值
        norm_delay = normalize(delay, delay_avg, delay_max, delay_min)
        norm_variance = normalize(variance, variance_avg, variance_max, variance_min)

        # 计算边的权重（这里简单地取两者的平均值）
        edge_weight = (norm_delay + norm_variance) / 2

        # 添加节点和边
        G.add_node(paths[0])
        G.add_node(paths[1])
        G.add_node(paths[2])
        G.add_edge(paths[0], paths[1], weight=edge_weight)
        G.add_edge(paths[1], paths[2], weight=edge_weight)

    return G



if __name__ == "__main__":
    # collect_read(f"{ROOT}\\data\\path_15.csv",f"{ROOT}\\data\\node_delay.csv")
    # file_path = f'{ROOT}/data/path.csv'
    # result = collect_read(file_path)
    # print(result)

    # clean_day2node(f"{ROOT}\\data\\day.csv",f"{ROOT}\\data\\node.csv")
    # clean_delay2node(f"{ROOT}\\data\\node_delay.csv",f"{ROOT}\\data\\node.csv")

    g_circuit = build_graph_from_csv(f"{ROOT}\\data\\path_15.csv")
    with open(f'{ROOT}\\pkl\\net_circuit.pkl', 'wb') as pkl_file:
        pickle.dump(g_circuit, pkl_file)