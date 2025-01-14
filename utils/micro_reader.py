import re
import sys
import base64
import pandas as pd
from collections import namedtuple
import os
from config import ROOT
import utils.json_saver
import utils.csv_gen

def identity2finger(identity):
    return base64.b64decode(identity + "=").hex()


def convert(row):
    identity = row.split()[2]
    date = row.split()[3]
    finger = identity2finger(identity).upper()
    row = row.replace(identity, finger)
    return row


def process_protocol(row):
    list = row.split(' ')
    Relay = ''
    FlowCtrl = ''
    HSDir = ''
    HSIntro = ''
    for l in list:
        if l.startswith('Relay'):
            Relay = l.split('=')[1]
        elif l.startswith('FlowCtrl'):
            FlowCtrl = l.split('=')[1]
        elif l.startswith('HSDir'):
            HSDir = l.split('=')[1]
        elif l.startswith('HSIntro'):
            HSIntro = l.split('=')[1]
    return Relay + ' ' + FlowCtrl + ' ' + HSDir + ' ' + HSIntro


def process_consensus(filename,csv_addr):
    # 数据处理
    global newlist, newlist, len
    with open(filename, 'r') as file:
        lines = file.readlines()
    # 过滤数据
    rdd_temp = [x.strip() for x in lines if
                re.match(r'r\s.*', x) or re.match(r's\s.*', x) or re.match(r'v\s.*', x) or re.match(r'w\s.*',                                                                        x) or re.match(
                    r'pr\s.*', x)]

    node_pattern = re.compile(r'r (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) (\S+)')
    res = []
    for i in range(0, len(rdd_temp), 5):
        nodes = {}
        if rdd_temp[i].startswith('r'):
            node_info = node_pattern.match(rdd_temp[i])
            if node_info:
                node = {
                    'nickname': node_info.group(1),
                    'identity_key': node_info.group(2),
                    'finger': identity2finger(node_info.group(2)).upper(),
                    'update_ymd': '0000-00-00',
                    'update_hms': node_info.group(4),
                    'ip': node_info.group(5),
                    'orport': int(node_info.group(6)),
                    'dirport': int(node_info.group(7)),
                }
                nodes['node'] = node
        if rdd_temp[i + 1].startswith('s'):
            flags = {
                'Authority': 0,
                'BadExit': 0,
                'Exit': 0,
                'Fast': 0,
                'Guard': 0,
                'Stable': 0,
                'V2Dir': 0,
                'HSDir': 0
            }
            keys = rdd_temp[i + 1].split(" ")
            for key in keys:
                if key in flags.keys():
                    flags[key] = 1
            nodes['flags'] = flags

        if rdd_temp[i + 2].startswith('v'):
            version = rdd_temp[i + 2].split(" ")[-1]
            nodes['version'] = version
        if rdd_temp[i + 3].startswith('w'):
            bandwidth = rdd_temp[i + 3].split(" ")[-1]
            nodes['bandwidth'] = bandwidth
        # if rdd_temp[i+4].startswith('pr'):
        #     print()
        res.append(nodes)

    utils.csv_gen.csv_day_write(csv_addr, res)
    # utils.json_saver.save_to_json(res, json_addr)

    return res


def get_all_consensus_files(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            if re.search('12-00-00', filename):
                # 获取相对路径
                # relative_path = os.path.relpath(os.path.join(root, filename), dir_path)
                # 获取绝对路径
                path = os.path.join(root, filename)
                file_list.append(path)
    return file_list


def merge_everyday(path):
    """
    取每天共识文件12点用于合成分析
    用于匹配ip和指纹的转换关系
    """
    res = get_all_consensus_files(path)  # res得到存放micro目录下所有文件的绝对路径
    print(len(res))
    print(res)
    sys.exit()
    # 创建一个名为 "合成.log" 的文件，以追加模式（'a+'）打开并使用UTF-8编码
    log = open(ROOT + "\\data" + "\\" + '合成day.log', 'a+', encoding='utf-8')

    for file in res:
        f = open(file, encoding='utf-8').read()
        log.write(f)
        log.flush()


def merge_everyhour(path):
    res = show_files(path)  # res得到存放micro目录下所有文件的绝对路径
    print(len(res))
    # 创建一个名为 "合成.log" 的文件，以追加模式（'a+'）打开并使用UTF-8编码
    log = open(ROOT + "\\data" + "\\" + '合成hour.log', 'a+', encoding='utf-8')

    for file in res:
        f = open(file, encoding='utf-8').read()
        log.write(f)
        log.flush()


def show_files(base_path, all_files=[]):
    # os.listdir() 用于列出目录中的所有文件和子目录。
    file_list = os.listdir(base_path)
    # 准备循环判断每个元素是否是文件夹还是文件，是文件的话，把名称传入list，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        # 如：os.path.join("/home/user/files", "data.csv") 得到完整路径 /home/user/files/data.csv。
        cur_path = os.path.join(base_path, file)
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            show_files(cur_path, all_files)
        else:
            all_files.append(cur_path)
    return all_files


if __name__ == "__main__":
    df = process_consensus("D:\\family_network\data\合成day.log",f'{ROOT}/data/day.csv')
    # # print(consensus_df)
