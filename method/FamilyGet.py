from contact_find import process_contact_family, process_micro_declared_family, read_res_csv, contact_method
from timeseq_find import process_timeseq_family1
from tool import last_month, download_detail, download_microdescs
from for_dump import read, fingerGet
from multigetinfo import mutigetinfo_run

output_path = "./output/"
finger_pkl = "./pkl/finger.pkl"
graph_pkl = "./pkl/graph.pkl"
node_csv = "./pkl/node.csv"
seq_pkl = "./pkl/seq.pkl"
res_csv = "./pkl/res.csv"
# 上个月的年月，以及上月的天数
year, month, day = last_month()
micro_path = f"./extracted_files/microdescs-{year}-{month}/micro"
descs_path = f"./downloads/{year}-{month}.tar.xz"
detail_path = "./downloads/details.json"

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

if __name__ == '__main__':
    """
    下载microdescs和details.txt
    可手动下载并按规则添加至对应文件夹
    """
    # month_str = f"{month:02d}"
    # url = f"https://collector.torproject.org/archive/relay-descriptors/microdescs/microdescs-{year}-{month}.tar.xz"
    # extract_to_folder = 'extracted_files'
    # download_microdescs(url, descs_path, extract_to_folder, proxies=proxies)
    # download_detail(detail_path, proxies=proxies)

    """
    预处理
    """
    read(f"./extracted_files/microdescs-{year}-{month}/consensus-microdesc/", day, finger_pkl, seq_pkl)
    print("step2 finish")
    fingerGet(finger_pkl, node_csv)
    print("step3 finish")
    mutigetinfo_run(res_csv, node_csv)
    print("step4 finish")

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
    g1, val1, _, _ = read_res_csv(g, res_csv, val,
                                  effective_family_or_not=True,
                                  micro_contact_family_or_not=False,
                                  )
    # 控制代码的运行情况
    Method_contact = True
    Method_timeseq = True

    if Method_contact:
        # 图连接关系混合contact图关系
        g_contact, _, val_contact, contact_finger_dict = read_res_csv(g, res_csv, val,
                                                                      effective_family_or_not=False,
                                                                           )
        # 得到基于contact识别的隐藏家族节点
        contact_method(contact_finger_dict, val1, val_contact, detail_path, output_path)

    print("step5 finish")
    '''
     方法2 依靠时序关系获取
     '''
    if Method_timeseq:
        process_timeseq_family1(seq_pkl, g, val1, detail_path, output_path)
