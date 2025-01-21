import csv
import os
import re
import sys

from config import ROOT
from utils.draw import draw_ip2finger
from utils.micro_reader import merge_everyday, process_consensus
from utils.json_saver import json_load
import ijson
import pandas as pd

hash_ip2finger = {}


def read_csv(filename):
    """
    逐步读取一个包含 node 和 flags 的 JSON 文件，并打印这些部分。

    :param filename: 输入的 JSON 文件路径
    """
    with open(filename, 'r', encoding='utf-8') as file:
        # 使用 ijson 逐步解析 JSON 文件中的对象
        reader = csv.DictReader(file)
        for row in reader:
            ip = row["ip"]
            finger = row["finger"]
            orport = row["orport"]
            add_fingerprint(ip, finger, orport)

    return hash_ip2finger


# 函数：添加 IP 和指纹的映射
def add_fingerprint(ip, finger, orport):
    # 如果该 IP 地址已经存在，则将新的指纹添加到对应的列表中
    ip_port = ip + ':' +orport
    # ip->指纹映射
    # if ip in hash_ip2finger:
    #     if finger not in hash_ip2finger[ip]:
    #         hash_ip2finger[ip].append(finger)
    # else:
    #     # 如果该 IP 地址不存在，创建一个新的列表并添加指纹
    #     hash_ip2finger[ip] = [finger]

    # ip + port ->指纹映射
    if ip_port in hash_ip2finger:
        if finger not in hash_ip2finger[ip_port]:
            hash_ip2finger[ip_port].append(finger)
    else:
        # 如果该 IP 地址不存在，创建一个新的列表并添加指纹
        hash_ip2finger[ip_port] = [finger]


def compare_ip_and_finger(filename, num):
    """
    :param filename: day.csv 位置
    :param num: 筛选改变指纹次数大于num的节点
    :return: res长度,list类型的ip列表
    """
    hash_ip2finger = read_csv(filename)
    res = dict_values_num(hash_ip2finger, num)
    return len(res), res


def dict_values_num(dict, num):
    """
    返回字典dict中，值数量大于等于num的keys
    """
    res = []
    for key, value in dict.items():
        if len(value) >= num:
            res.append(key)
    return res


def anlysis_HDSir(ip_list, csv_file):
    """
    抓取改变指纹次数大于5的节点，观察他们的HDSir flag变化
    :return:
    """
    df = pd.read_csv(csv_file)
    result = []

    for ip_port in ip_list:
        # 分离出 IP 和端口
        ip, port = ip_port.split(':')
        port = int(port)  # 转换端口为整数

        # 在 DataFrame 中查找 IP 和 port 一致的行
        matching_rows = df[(df['ip'] == ip) & (df['orport'] == port)]  # 假设 'ip' 和 'orport' 是列名

        if not matching_rows.empty:
            # 如果找到了符合条件的行，提取 HSDir 列并以 {'ip:port':, 'HSDir':} 格式保存
            hsdir_values = matching_rows['HSDir'].tolist()
            result.append({'ip:port': ip_port, 'HSDir': hsdir_values})
        else:
            print(f"No matching rows found for IP: {ip} and Port: {port}")

    return result


if __name__ == "__main__":
    # 合成day.log
    merge_everyday('E:\\family_network\download\microdescs-2024-11\consensus-microdesc')
    # 生成day.csv
    df = process_consensus("E:\\family_network\data\合成day.log", f'{ROOT}/data/day1.csv')

    # 画图
    # hash_ip2finger = read_csv("D:\\family_network\data\day.csv")
    # n_values = range(1, 11)
    # counts = [len(dict_values_num(hash_ip2finger, n)) for n in n_values]
    # draw_ip2finger(f'{ROOT}//picture//ip_port2finger.png', counts)

    # 寻找大于5的节点
    # _, lists = compare_ip_and_finger("D:\\family_network\data\day.csv", 4)
    # print(lists)
    #
    # HDsir_list = anlysis_HDSir(lists,"D:\\family_network\data\day.csv")
    # print(HDsir_list)

    # 2节点 185.112.249.156:443
    # 4节点 93.160.17.86:9025
    # 5节点 45.14.165.118:9001
