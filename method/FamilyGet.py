import pickle

import networkx as nx

from contact_find import process_contact_family, process_micro_declared_family, read_res_csv, contact_method
from timeseq_find import process_timeseq_family1
from tool import last_month, download_detail, download_microdescs
from for_dump import read, fingerGet
from multigetinfo import mutigetinfo_run
from config import ROOT
import tarfile
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import igraph as ig
from pyvis.network import Network

output_path = f"{ROOT}/output/"
finger_pkl = f"{ROOT}/pkl/finger.pkl"
graph_pkl = f"{ROOT}/pkl/graph.pkl"
node_csv = f"{ROOT}/pkl/node.csv"
seq_pkl = f"{ROOT}/pkl/seq.pkl"
res_csv = f"{ROOT}/pkl/res.csv"
# 上个月的年月，以及上月的天数
year, month, day = last_month()
micro_path = f"{ROOT}/download/microdescs-{year}-{month}/micro"
descs_path = f"{ROOT}/download/{year}-{month}.tar.xz"
detail_path = f"{ROOT}/download/details.json"

'''
数据来源获取，主要分为detail和两个共识文件
# 下载地址：https://metrics.torproject.org/collector/archive/relay-descriptors/microdescs/
通过utils自动下载解压，或手动下载
你需要代理才能访问这两个网址
'''
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

# 如果当前网络环境能直接访问外网
# proxies = None

def merge_net(g_f, g_c, g_s, weight_f, weight_c, weight_s):
    """
    将三个图融合成一个新图，并根据给定的权重调整边的权重。

    参数:
    g_f (networkx.Graph): 第一个图
    g_c (networkx.Graph): 第二个图
    g_s (networkx.Graph): 第三个图
    weight_f (float): 第一个图的边权重系数
    weight_c (float): 第二个图的边权重系数
    weight_s (float): 第三个图的边权重系数

    返回:
    networkx.Graph: 融合后的图
    """
    # 创建一个新的图来存储融合后的结果
    g_total = nx.Graph()

    # 定义一个辅助函数来添加图的节点和边到新图中
    def add_graph_to_total(g, weight):
        # 添加节点
        g_total.add_nodes_from(g.nodes())
        # 添加边，并根据权重调整边的权重
        for u, v, data in g.edges(data=True):
            if 'weight' in data:
                new_weight = data['weight'] * weight
            else:
                new_weight = weight
            if g_total.has_edge(u, v):
                g_total[u][v]['weight'] += new_weight
            else:
                g_total.add_edge(u, v, weight=new_weight)

    # 依次添加三个图到新图中
    add_graph_to_total(g_f, weight_f)
    add_graph_to_total(g_c, weight_c)
    add_graph_to_total(g_s, weight_s)

    return g_total


if __name__ == '__main__':
    """
    下载microdescs和details.txt
    可手动下载并按规则添加至对应文件夹
    """
    # month_str = f"{month:02d}"
    # url = f"https://collector.torproject.org/archive/relay-descriptors/microdescs/microdescs-{year}-{month}.tar.xz"
    # extract_to_folder = f'{ROOT}//download'
    # download_microdescs(url, descs_path, extract_to_folder, proxies=proxies)
    # download_detail(detail_path, proxies=proxies)
    """
    预处理
    """
    # 解压
    # with tarfile.open(f"{ROOT}\\download\\microdescs-2024-11.tar.xz", 'r:xz') as tar_ref:
    #     tar_ref.extractall(f"{ROOT}\\download")

    # read(f"{ROOT}/download/microdescs-{year}-{month}/consensus-microdesc/", day, finger_pkl, seq_pkl)
    # # read(f"./download/microdescs-{year}-{month}/consensus-microdesc/", day, finger_pkl, seq_pkl)
    # print("step2 finish")
    # fingerGet(finger_pkl, node_csv)
    # print("step3 finish")
    # mutigetinfo_run(res_csv, node_csv)
    # print("step4 finish")

    '''
     方法1 依靠一致关系获取
    # process_contact_family 包含两个部分：
    process_contact_family(micro_path, res_csv) 负责处理micro文件
    1、合成micro文件
    2、通过micro文件过滤出micro中所有节点的family->list
    3、get_family(list)---> 1、对于相同家族的成员两两进行边连关系形成一个图
                            2、返回g,val g为图，val为图的连通分量集，一个连通分量为一个家族
    返回值：g, val, list list为所有存在的家族list 

    read_res_csv 负责处理details文件
    使用res.csv处理contact列进行过滤提取，连接形成contact_finger_dict 
    contact_finger_dict经过get_family(dict)处理，形成contact家族
    返回值：val2, contact_finger_dict：val2同val，contact_finger_dict为contact和指纹的映射关系
    '''

    # # 连接基本声明家族 第三个参数用于find_big_family() 这里用不到
    g, val, _ = process_micro_declared_family(micro_path)
    # 此时得到的的g为声明家族图，val1为[家族序号，家族节点]
    g_family, val_family, _, _ = read_res_csv(g, res_csv, val,
                                  effective_family_or_not=True,
                                  micro_contact_family_or_not=False,
                                  )
    # 控制代码的运行情况
    Method_contact = True
    Method_timeseq = True


    # 图连接关系混合contact图关系
    g_contact, _, val_contact, contact_finger_dict = read_res_csv(nx.Graph(), res_csv, None,
                                                                  effective_family_or_not=False,
                                                                       )
    # 得到基于contact识别的隐藏家族节点
    # contact_method(contact_finger_dict, val1, val_contact, detail_path, output_path)

    print("step5 finish")
    '''
     方法2 依靠时序关系获取
    '''
    g_seq,val_seq = process_timeseq_family1(seq_pkl, nx.Graph(), None, detail_path, output_path)

    g_total = merge_net(g_family,g_contact,g_seq,0.6,0.3,0.1)

    with open(f'{ROOT}\\pkl\\net.pkl', 'wb') as pkl_file:
        pickle.dump(g_total, pkl_file)


    # # 使用 graphviz 布局
    # pos = graphviz_layout(g_total, prog='dot')
    #
    # # 绘制图
    # nx.draw(g_total, pos, with_labels=True, node_size=100, font_size=8)
    #
    # # 显示图像
    # plt.show()

    # # 创建一个 pyvis 网络对象
    # net = Network(notebook=True)
    #
    # # 从 networkx 图中添加节点和边
    # net.from_nx(g_total)
    #
    # # 设置一些可视化选项
    # net.show_buttons(filter_=['physics'])
    #
    # # 保存为 HTML 文件
    # net.show('network.html')