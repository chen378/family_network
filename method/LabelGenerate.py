import numpy as np
import pandas as pd

from config import ROOT


def normalize_column(column):
    """
    对列进行归一化处理。

    :param column: 输入的列数据
    :return: 归一化后的列数据
    """
    min_val = column.min()
    max_val = column.max()
    return (column - min_val) / (max_val - min_val)


def assign_labels(csv_file):
    """
    读取 CSV 文件，对 delay 和 variance 进行归一化，计算加权得分，并为前 20% 的节点分配 label 为 1，其余为 0。

    :param csv_file: CSV 文件的路径
    :return: 带有 label 列的 DataFrame
    """
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)

    # 对 delay 和 variance 进行归一化处理
    df['delay_normalized'] = normalize_column(df['delay'])
    df['variance_normalized'] = normalize_column(df['variance'])

    # 假设 delay 和 variance 同等重要，计算加权得分
    df['weighted_score'] = (df['delay_normalized'] + df['variance_normalized']) / 2

    # 找出加权得分的第 80 百分位数
    threshold = df['weighted_score'].quantile(0.8)

    # 为节点分配 label
    df['label'] = np.where(df['weighted_score'] >= threshold, 1, 0)

    # 将 label 写回原表
    df.to_csv(csv_file, index=False)

    return df


if __name__ == "__main__":
    csv_file = f'{ROOT}\\data\\node.csv'   # 请将此路径替换为你的 node.csv 文件的实际路径
    labeled_df = assign_labels(csv_file)
    print(labeled_df)

