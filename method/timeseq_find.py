import pickle
import networkx as nx
from tqdm import tqdm
import json
import csv


# import A_delete
def get_components(g):
    k = 0
    val = []
    for e in nx.connected_components(g):
        if len(e) > 1:  # 连通分量>1 说明存在家族关联
            for n in e:
                val.append([k, n])
            k += 1
    return val


# def get_family(g=None, list=None, dict=None):
#     if g == None:
#         g = nx.Graph()
#     if list != None:
#         for sub_list in list:
#             for i in range(len(sub_list) - 1):  # family字段不止一个，存在家族
#                 g.add_edge(sub_list[i][1:],
#                            sub_list[i + 1][1:])  # 纳入联通分量。sub_list[x][y]x:表示坐标，y：表示截取的长度。从1开始是每个指纹前面都有一个$符号，从1取到末尾
#     if dict != None:
#         for value in dict.values():
#             for i in range(len(value) - 1):  # family字段不止一个，存在家族
#                 g.add_edge(value[i], value[i + 1])  # 纳入联通分量
#     val = get_components(g)
#     return g, val

def get_family(g=None, dict=None, list=None):
    if g == None:
        g = nx.Graph()
    if dict != None:
        for value in dict.values():
            for i in range(len(value) - 1):  # family字段不止一个，存在家族
                g.add_edge(value[i], value[i + 1])  # 纳入联通分量
    if list != None:
        for sub_list in list:
            for i in range(len(sub_list) - 1):  # family字段不止一个，存在家族
                g.add_edge(sub_list[i].upper(), sub_list[i + 1].upper())  # 纳入联通分量
    val = get_components(g)
    return g, val


def process_timeseq_family1(seq_pkl, g, val, detail_path, output_path):
    # 处理seq时间序列，seq格式为[(序列,同序列的指纹)]
    with open(seq_pkl, 'rb') as f:
        seq_val = pickle.load(f)
    fingerL = []
    for (xulie, fingerList) in seq_val:
        if xulie.count('0') == 0 or xulie.count('1') == 0:
            continue
        fingerL.append(fingerList)
    g, val2 = get_family(g=g, list=fingerL)
    return g,val2

    # val_clear = []
    # for i in val:
    #     val_clear.append(i[1])
    # res = []  # 用于后续到数据库中删除指定内容
    # count_hidden = 0
    # count_public = 0
    # results = []
    # for fanum, fingerprint in tqdm(val2, total=len(val2)):
    #     # 如果找到隐藏家族节点
    #     if fingerprint not in val_clear:
    #         count_hidden += 1
    #         hidden_family = 1
    #     else:
    #         count_public += 1
    #         hidden_family = 0
    #         # continue
    #
    #     or_addresses = ""
    #     contact = ""
    #     res.append(fingerprint)
    #     for (xulie, fingerList) in seq_val:
    #         if fingerprint.lower() in fingerList:
    #             XL = xulie
    #             fingerlist = [item.upper() for item in fingerList]
    #
    #     with open(detail_path, 'r', encoding='utf-8') as f:
    #         relays = json.load(f)["relays"]
    #         for relay in relays:
    #             if relay.get("fingerprint") == fingerprint:
    #                 or_addresses = relay.get("or_addresses", "")
    #                 contact = relay.get("contact", "")
    #                 break
    #
    #     results.append([or_addresses, fingerprint, contact, fanum, hidden_family])
    #
    # print(f"查询完成，共识别出{count_hidden}个隐藏家族节点")
    #
    # if results:
    #     with open(output_path + "method_2.csv", 'w', newline='', encoding='utf-8') as csvfile:
    #         writer = csv.writer(csvfile)
    #         writer.writerow(['or_addresses', 'fingerprint', 'contact', 'fanum', 'hidden_family'])  # 写入表头
    #         writer.writerows(results)  # 写入数据
    #     print(f"信息已保存至 {output_path}")
