# 把finger和seq序列化本地放置
import csv
import os
import extractTor
import pickle


def read(parent_path, day_num, finger_pkl, seq_pkl):
    last_dict = dict()
    # 创建字典，遍历文件
    for day in range(1, day_num + 1):
        if day < 10:
            subfolder = '0' + str(day)
        else:
            subfolder = str(day)

        path = parent_path + subfolder
        files = os.listdir(path)

        for hour in range(len(files)):
            cur_dict = dict()
            f = open(path + "/" + files[hour], 'r')
            extractTor.the_data_handler(f.name, day, hour, last_dict, cur_dict)
            f.close()
            last_dict = cur_dict

    with open(finger_pkl, 'wb') as f:
        pickle.dump(cur_dict, f)
    # 序列为键，节点为val
    # 这里需要处理出一个node字典

    seq_finger_dict = dict()
    for k, v in cur_dict.items():
        if seq_finger_dict.__contains__(v):
            old_v = seq_finger_dict[v]
            old_v.append(k)
            seq_finger_dict[v] = old_v
        else:
            seq_finger_dict[v] = [k]
    sorted_res = sorted(seq_finger_dict.items(), key=lambda x: len(x[1]), reverse=True)

    with open(seq_pkl, 'wb') as f:
        pickle.dump(sorted_res, f)


def fingerGet(fingerpkl_path, target_path):
    global finger
    f = open(fingerpkl_path, 'rb')
    # 这里的finger是一个字典，我们需要：1、遍历字典的key,2、转换为大写，3、写入node.csv
    fingerseq = pickle.load(f)
    fingerList = []
    for finger in fingerseq.keys():
        fingerList.append(finger.upper())
    # print(fingerList)
    # 这里得到的test.csv为一个月出现的所有节点的指纹
    with open(target_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(["finger"])
        # 逐行写入数据，并去掉引号
        for item in fingerList:
            writer.writerow([item])
