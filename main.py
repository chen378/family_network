# 这是一个示例 Python 脚本。
import os
from config import ROOT
from method.CircuitAnlysis import build_graph_from_csv, circuit_net_generate, collect_read, clean_day2node, \
    clean_delay2node
from method.FamilyGet import family_net_generate
from method.LabelGenerate import assign_labels
from utils.csv_gen import merge_csv_circuit
from utils.download_micro import MicroDownload,last_month
from utils.micro_reader import process_consensus, merge_everyday

year, month, day = last_month()
month_str = f"{month:02d}"
descs_path = f"./download/{year}-{month_str}.tar.xz"
extract_to_folder = f"./download"
output_path = f"{ROOT}/output/"
finger_pkl = f"{ROOT}/pkl/finger.pkl"
graph_pkl = f"{ROOT}/pkl/graph.pkl"
node_csv = f"{ROOT}/pkl/node.csv"
seq_pkl = f"{ROOT}/pkl/seq.pkl"
res_csv = f"{ROOT}/pkl/res.csv"
# 上个月的年月，以及上月的天数
micro_path = f"{ROOT}/download/microdescs-{year}-{month}/micro"
detail_path = f"{ROOT}/download/details.json"

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':

    """
    下载数据
    """

    MicroDownload(descs_path, extract_to_folder)

    """
    数据处理
    """
    # 获得多天的链路信息
    merge_csv_circuit(f"{ROOT}\\download\\circuit_json_15", f"{ROOT}\\data\\path_15.csv")

    # 合成day.log
    merge_everyday(f'{ROOT}\\microdescs-{year}-{month}\\consensus-microdesc')
    # 从合成的共识文件中获取节点数据存放到day.csv中
    df = process_consensus(f"{ROOT}\\data\\合成day.log",f'{ROOT}/data/day.csv')


    """
    数据合并
    """

    collect_read(f"{ROOT}\\data\\path_15.csv",f"{ROOT}\\data\\node_delay.csv")
    clean_day2node(f"{ROOT}\\data\\day.csv",f"{ROOT}\\data\\node.csv")
    clean_delay2node(f"{ROOT}\\data\\node_delay.csv",f"{ROOT}\\data\\node.csv")



    """
    生成标签
    """
    labeled_df = assign_labels(f'{ROOT}\\data\\node.csv')


    """
    生成图
    """
    # net.pkl 生成 融合了seq、contact、family家族权值
    family_net_generate()

    # net_circuit.pkl 生成 将现有的所有随机链路连线，以带宽和
    path_merge_csv = f"{ROOT}\\data\\path_15.csv"
    circuit_net_generate(path_merge_csv)

    # 图融合

    """
    图神经网络
    """
    # 得到的结果与直接筛选做对比 与 不筛选做对比