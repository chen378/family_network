import csv
import json
import time
import pickle
from utils import postfor_info
from node import node
from tqdm import tqdm


# 从nodefinger10.csv读取所有待处理节点指纹，多进程爬取历史日志中不包含的节点信息，并写入res1.csv中
def read_finger(node_csv):
    node_list = []
    with open(node_csv) as f:
        count = 0
        f_csv = csv.reader(f)
        for row in f_csv:
            count += 1
            mynode = node(row[0])
            node_list.append(mynode)
    return node_list, count


def dopost(node_list, json_file="./downloads/details.json"):
    res_list = []
    with open(json_file, 'r', encoding='utf-8') as f:
        relays = json.load(f)["relays"]
        for i, node in tqdm(enumerate(node_list), total=len(node_list), desc="Processing nodes", unit="node"):
            postfor_info(node, relays)
            res_list.append(
                [node.finger, node.asinfo, node.exit_policy, node.contact, node.alleged_family, node.effective_family,
                 node.indirect_family])
    return res_list


def write_res(res_csv, res_list):
    with open(res_csv, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["finger", "asinfo", "exit_policy", "contact", "alleged_family", "effective_family", "indirect_family"])
        row = res_list
        for r in row:
            writer.writerow(r)
    print("finish")
    return


def list_of_groups(init_list, children_list_len):
    list_of_groups = zip(*(iter(init_list),) * children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count != 0 else end_list
    return end_list


def mutigetinfo_run(res_csv, node_csv):
    global count
    start = time.time()
    node_list, count = read_finger(node_csv)
    result = dopost(node_list)

    with open(res_csv[:-3]+".pkl", 'wb') as f:
        pickle.dump(result, f)

    with open(res_csv[:-3]+".pkl", 'rb') as f:
        all_list = pickle.load(f)

    write_res(res_csv, all_list)

    print(f"It takes {time.time() - start} seconds!")


