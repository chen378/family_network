import pandas as pd
from config import ROOT


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

    # 以fingerprint（path_str）为主键
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



# def split_and_aggregate_pandas(out_csv, node_delay_csv):


if __name__ == "__main__":
    collect_read(f"{ROOT}\\data\path_15.csv",f"{ROOT}\\data\\node_delay.csv")
    # file_path = f'{ROOT}/data/path.csv'
    # result = collect_read(file_path)
    # print(result)
