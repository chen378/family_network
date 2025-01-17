import json
import csv
import os
from config import ROOT

# def csv_circuit(json_data_file, out_csv):
#     # 获取当前脚本所在的目录
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     # 构建 data 文件夹的相对路径
#     data_dir = os.path.join(script_dir, '..', 'data')
#     # 构建 JSON 文件的完整路径
#     json_file_path = os.path.join(data_dir, json_data_file)
#     # 构建 CSV 文件的完整路径
#     csv_file_path = os.path.join(data_dir, out_csv)
#
#     with open(json_file_path, 'r') as file:
#         json_data = file.read()
#     data = json.loads(json_data)  # 将 JSON 字符串解析为 Python 对象
#     results = data['results']  # 获取 results 列表
#
#     headers = ['delay', 'variance', 'path_str', 'ip_str', 'time']
#     with open(csv_file_path, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=headers)
#         writer.writeheader()  # 写入表头
#         for result in results:  # 遍历 results 列表中的每个元素
#             # 提取所需的数据并写入 CSV 文件
#             row = {
#                 'delay': result['delay'],
#                 'variance': result['variance'],
#                 'path_str': result['path_str'],
#                 'ip_str': result['ip_str'],
#                 'time': result['time']
#             }
#             writer.writerow(row)

def csv_circuit(json_data_file, out_csv):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    json_file_path = os.path.join(data_dir, json_data_file)
    csv_file_path = os.path.join(data_dir, out_csv)

    with open(json_file_path, 'r') as file:
        json_data = file.read()
    data = json.loads(json_data)
    results = data['results']

    headers = ['delay', 'variance', 'path_str', 'ip_str', 'time']
    with open(csv_file_path, 'w' if not os.path.exists(csv_file_path) else 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if csvfile.tell() == 0:  # 仅当文件为空时写入表头
            writer.writeheader()
        for result in results:
            row = {
                'delay': result['delay'],
                'variance': result['variance'],
                'path_str': result['path_str'],
                'ip_str': result['ip_str'],
                'time': result['time']
            }
            writer.writerow(row)


def merge_csv_circuit(file_addr, out_csv):
    # 遍历 file_addr 目录下的所有文件
    for root, dirs, files in os.walk(file_addr):
        for file in files:
            if file.endswith('.json'):
                json_file = os.path.join(root, file)
                csv_circuit(json_file, out_csv)


def csv_day_write(filename, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        # 定义 CSV 表头
        fieldnames = [
            "nickname", "identity_key", "finger", "update_ymd", "update_hms",
            "ip", "orport", "dirport",
            "Authority", "BadExit", "Exit", "Fast", "Guard", "Stable", "V2Dir", "HSDir", "version"
        ]

        # 创建 CSV 写入对象
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()

        # 将数据转换为适合 CSV 格式的字典
        for obj in data:
            node = obj['node']
            flags = obj['flags']
            row = {
                "nickname": node['nickname'],
                "identity_key": node['identity_key'],
                "finger": node['finger'],
                "update_ymd": node['update_ymd'],
                "update_hms": node['update_hms'],
                "ip": node['ip'],
                "orport": node['orport'],
                "dirport": node['dirport'],
                "Authority": flags['Authority'],
                "BadExit": flags['BadExit'],
                "Exit": flags['Exit'],
                "Fast": flags['Fast'],
                "Guard": flags['Guard'],
                "Stable": flags['Stable'],
                "V2Dir": flags['V2Dir'],
                "HSDir": flags['HSDir'],
                "HSDir": flags['HSDir'],
                "version": obj['version']
            }
            writer.writerow(row)


if __name__ == "__main__":
    # csv_circuit('collect_result.json', 'path.csv')
    merge_csv_circuit(f"{ROOT}\\download\\circuit_json_15","path_15.csv")