import pandas as pd
from config import ROOT


# 读取 collect.json文件
def collect_read(file_path, Ff=True, Sf=True, Tf=True):
    """
    读取生成collect表单的统计信息，统计节点出现频次
    """
    # 读取 CSV 文件
    df = pd.read_csv(file_path)
    # 获取 ip_str 列
    ip_str_column = df['ip_str']
    # 存储所有 IP 地址的列表
    all_ips = []

    for entry in ip_str_column:
        ips = entry.split(' ')
        all_ips.extend(ips)

    ip_counts = {}
    for ip in all_ips:
        if ip in ip_counts:
            ip_counts[ip] += 1
        else:
            ip_counts[ip] = 1

    frequent_ips = {}
    for ip, count in ip_counts.items():
        if count > 7:
            frequent_ips[ip] = count
    return frequent_ips


if __name__ == "__main__":
    file_path = f'{ROOT}/data/path.csv'
    result = collect_read(file_path)
    print(result)
