import json
import ijson

def save_to_json(data, filename):
    """
    data 为内容
    filename为存放的位置
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def json_load(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data






import ijson

def read_json_in_stream(filename):
    """
    逐步读取一个包含 node 和 flags 的 JSON 文件，并打印这些部分。

    :param filename: 输入的 JSON 文件路径
    """
    with open(filename, 'r', encoding='utf-8') as file:
        # 使用 ijson 逐步解析 JSON 文件中的对象
        objects = ijson.items(file, 'node')  # 逐步读取 'node' 部分
        for obj in objects:
            # 每个 obj 是一个 node 部分
            print("Node:")
            print(f"Nickname: {obj['nickname']}")
            print(f"Identity Key: {obj['identity_key']}")
            print(f"IP: {obj['ip']}")
            print(f"OR Port: {obj['orport']}")
            print(f"DIR Port: {obj['dirport']}")




