import copy
import csv
import os
import re
import sys

from tqdm import tqdm
import networkx as nx
import logging
import json

# 用于处理合成日志的信息，得到所有家族相关的列表
'''
这个函数首先使用 SparkContext 对象读取日志文件，然后使用 filter() 函数过滤出所有以 "family $" 开头的行，再使用 map() 函数对行进行处理。
处理后的结果是一个包含家族信息的列表。最后，该函数返回这个列表。
'''


def process_log(micro_path):
    '''
    这个函数读取日志文件并过滤符合特定条件的行，然后对每行进行处理，最终返回一个列表。
    '''
    log_path = micro_path + '\\' + '合成.log'
    result = []

    with open(log_path, 'r', encoding='utf-8') as file:
        # 遍历文件中的每一行
        for line in file:
            # 使用正则表达式过滤出以 'family $' 开头的行
            if re.match(r'family \$.*', line):
                # 去掉 'family $' 之前的部分并按空格分割
                parts = line[7:].split()
                result.append(parts)  # 将处理后的结果添加到结果列表

    return result


# 根据指定的 SQL 语句类型，将 val 中的值插入到 MySQL 数据库中。
'''
finger: 存储节点的指纹（fingerprint）。
contact: 存储节点的联系信息。
asinfo: 存储节点的 AS 信息（自治系统信息）。
exit_policy: 存储节点的退出策略。
micro_declared_family: 存储基于微观声明的家族信息。
micro_contact_declared_family: 存储基于联系声明的家族信息。
onionoo_declared_family: 存储 Onionoo 声明的家族信息。
onionoo_indirect_declared_family: 存储 Onionoo 声明的间接家族信息。
real_family: 存储实际家族信息。
'''


# 从图 g 中获取连通分量，并返回一个包含家族编号和节点指纹的列表。
def get_components(g):
    k = 1
    val = []
    '''
    nx.connected_components:返回的是一个生成器，生成图 G 中的所有连接组件。每个连接组件都是一个包含顶点的集合。
    # 创建一个简单的无向图
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (4, 5)])
    #计算图中的连接组件
    connected_components = list(nx.connected_components(G))
    #打印连接组件
    print(connected_components)    [{1, 2, 3}, {4, 5}]
    '''
    for e in nx.connected_components(g):
        if len(e) > 1:  # 连通分量>1 说明存在家族关联，并且也进行了处理。
            for n in e:
                val.append([k, n])
            k += 1
    return val


# 根据输入的列表或字典，构建一个网络图来表示节点间的家族关系，并返回连通分量列表。
'''
这个函数的输入参数包括一个图（默认为 None），一个列表（默认为 None），一个字典（默认为 None）。
如果提供了列表，则函数会遍历列表中的每个子列表，并将列表中的所有节点添加到图中。
如果提供了字典，则函数会遍历字典中的所有值，并将每个值中的所有节点添加到图中。

在图中，如果存在多个联通分量，那么说明这些节点之间有家族关系。
因此，这个函数使用 NetworkX 库计算图中的连通分量，并返回包含每个联通分量的列表。
每个联通分量是由其节点组成的列表，每个节点用其名称标识。
'''


def get_family(g=None, list=None, dict=None):
    if g is None:
        # nx.Graph() 是 NetworkX 库中用于创建一个空的、无向图的方法。该方法返回一个无向图对象，可以向这个对象中添加节点和边。
        # 可以使用 g.add_node() 和 g.add_edge() 方法添加节点和边到这个图中。
        g = nx.Graph()
    '''
    这里会存在一个现象，sub_list是每一个家族，他们会得到一个单独的图，但是有许多sub_list这样的小家族，他们之间是会存在重复的节点，这样在连边的时候，就会使得原本独立的小家族之间会连接起来。
    举例例子：A家族中1-2-3-4，但是B家族出现2-7-8.那么是不是就出现了A，B两个小家族进行连接的情况。
    '''
    if list is not None:
        for sub_list in list:
            for i in range(len(sub_list) - 1):  # family字段不止一个，存在家族
                g.add_edge(sub_list[i][1:],
                           sub_list[i + 1][1:])  # 纳入联通分量。sub_list[x][y]x:表示坐标，y：表示截取的长度。从1开始是每个指纹前面都有一个$符号，从1取到末尾
    if dict is not None:
        for value in dict.values():
            for i in range(len(value) - 1):  # family字段不止一个，存在家族
                g.add_edge(value[i], value[i + 1])  # 纳入联通分量
    '''
    get_components() 用来获取图中所有的联通分量。
    给定一个图对象 g，则 get_components(g) 将返回一个列表，其中每个元素都是一个列表，包含一个节点的标识符和它所属的联通分量标识符。
    函数遍历图中的每个连通分量，并为每个连通分量创建一个唯一的标识符 k。
    然后，对于图中的每个节点，函数会检查其所在的联通分量，并将该节点的标识符和唯一的连通分量标识符（即 k）添加到一个列表中。
    最后，函数返回一个列表，其中包含所有节点的标识符和它们所属的联通分量标识符。

    你可以在value下面进行debug一下，就可以看出val其实就是一个列表，里面对是同一个家族进行了相同的编号。
    怎么判断是同一个家族，其实就是对图g的判断。图g里面有很多个连通子图，每个连通子图连边都是连边的，也就是一个家族。
    '''
    val = get_components(g)
    return g, val


# 遍历micro目录下面的所有文件和文件夹，并返回一个包含所有文件路径的列表。
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


# 将path（就是micro）下的文件 合成.log。
def merge(path):
    res = show_files(path)  # res得到存放micro目录下所有文件的绝对路径
    print(len(res))
    # 创建一个名为 "合成.log" 的文件，以追加模式（'a+'）打开并使用UTF-8编码
    log = open(path + "\\" + '合成.log', 'a+', encoding='utf-8')

    for file in res:
        f = open(file, encoding='utf-8').read()
        log.write(f)
        log.flush()


def deal(list):
    res = []
    for sub_list in list:
        tmp = []
        for i in sub_list:
            if (len(i) == 41):
                tmp.append(i)
        res.append(tmp)
    return res


# 处理和分析 micro 声明的家族关系，返回一个网络图和家族编号及节点指纹的列表。
def process_micro_declared_family(micro_path):
    if not os.path.exists(micro_path + "\\" + '合成.log'):
        merge(micro_path)
        print("finish")

    # 用于配置日志记录的基本行为,设置日志记录器的默认级别为 INFO，意味着只有等于或高于 INFO 级别的日志才会被输出。
    # 不写这个函数，就需要在代码中显式地创建一个 logger 对象，然后对其进行配置
    logging.basicConfig(level=logging.INFO)
    print("start process_log")
    tmp = process_log(micro_path)  # 处理合成.log文件，得到所有家族的list表。 从得到初始的表
    list = deal(tmp)  # 剔除那些不是指纹的信息 长度为41的才是指纹

    '''
    对得到的家族节点列表进行连边处理，得到一个包含许多连通子图的图g，以及进过对连通子图进行处理并赋予其编号。
    '''
    g, val = get_family(list=list)
    return g, val, list


# 读取节点家族关系的 CSV 文件，并将结果插入到 MySQL 数据库中。
def read_res_csv(g,  # micro 生成的图
                 res_csv,
                 row_val,  # 对应 [家族编号，finger]列表
                 effective_family_or_not=True,
                 micro_contact_family_or_not=True,
                 ):
    # 下面三个是图对象
    g_all = copy.deepcopy(g)  # 对传入的图对象g进行深拷贝，创建了一个完全独立的副本，不与原始图共享任何数据结构。g_all将用于存储包括传入图g在内的所有家族关系。
    g_onion = nx.Graph()  # 创建一个新的空图对象，用于存储Onionoo声明的家族关系                            对应数据库中的onionoo_declared_family
    g_onion_with_indirect = nx.Graph()  # 创建另一个新的空图对象，用于存储Onionoo声明的间接家族关系            对应数据库中的onionoo_indirect_declared_family
    # 下面是四个字典，用于存储数据。
    contact_finger_dict = {}  # 对应数据库中的 micro_contact_declared_family
    finger_not_family_dict = {}
    finger_effective_family_dict = {}
    finger_indirect_family_dict = {}
    # 三个队列,对应到下面的csv文件的获取的数据
    # node_list = []
    val_contact = []  # 对应数据库中的contact
    val_as = []  # 对应着数据库的asinfo
    val_exitpolicy = []  # 对应着数据库中的exit_policy

    val_res = []  # 返回回去

    '''
    now_res.csv文件里面的内容
    finger,asinfo,exit_poicy,contact,alleged_family,effective_family,indirect_family
    这个大块就是将now_res.csv文件里面的内容进行了拆分为一个一个的模块，不过每个模块都是有自己的方式。可以看每一个模块的最后一行代码就现实的比较清除。
    '''
    with open(res_csv, "r", encoding="utf-8") as f:
        f_csv = csv.reader(f)  # 将从f文件对象中读取数据
        headers = next(f_csv)  # 读取CSV文件的第一行并将其存储在变量headers中
        for row in f_csv:
            finger = row[0]
            asinfo = row[1]
            if asinfo != '' and asinfo != 'null':
                val_as.append([asinfo, finger])

            exit_policy = row[2]
            if exit_policy != '' and exit_policy != 'null' and exit_policy != '[]':
                val_exitpolicy.append([str(exit_policy), finger])

            contact = row[3]
            # 反斜线（\）是一个续行符。它用于表示一行代码太长，需要在多行上分布
            if contact != '' \
                    and contact != 'null' \
                    and contact != 'tor-operator@your-emailaddress-domain' \
                    and contact != 'your@e-mail' \
                    and contact != 'your@e-mail.com' \
                    and contact != 'your@email.com' \
                    and contact != 'none' \
                    and contact != 'None':

                if "proof:" in contact:
                    # rfind() 方法用于在字符串中从右边开始查找子字符串的最后一次出现。如果找到子字符串，则返回子字符串第一个字符的索引；如果没有找到子字符串，返回-1
                    idx = contact.rfind('proof:')
                    contact = contact[:idx]  # 只保留proof之前的内容，后面的不需要
                val_contact.append([contact, finger])
                '''
                作用是将联系人（contact）和对应的指纹（finger）关联起来并存储在一个字典（contact_finger_dict）中。有点像哈希表的形式
                首先检查contact_finger_dict字典中是否已经包含了当前联系人（contact）的键。如果包含：
                    a. 从字典中获取与该联系人相关联的指纹列表（old_v）。
                    b. 将当前指纹（finger）添加到指纹列表（old_v）中。
                    c. 将更新后的指纹列表重新存储到字典中，用联系人（contact）作为键。
                如果字典中没有包含该联系人（contact）：
                    a. 创建一个新的空列表（v）。                
                    b. 将当前指纹（finger）添加到新的列表中。                    
                    c. 将新的指纹列表存储到字典中，用联系人（contact）作为键。                
                最终，contact_finger_dict 字典将包含每个联系人及其对应的指纹列表。

                val_contact列表：一个contact对应一个finger，一一对应；
                contact_finger_dict[contact,duoge finger]列表是：一个contact对应着多个finger，一对多；
                '''
                if contact_finger_dict.__contains__(contact):
                    old_v = contact_finger_dict[contact]
                    old_v.append(finger)
                    contact_finger_dict[contact] = old_v
                else:
                    v = []
                    v.append(finger)
                    contact_finger_dict[contact] = v

            alleged_family = row[4]
            '''
            alleged_family虽然没有在now_res.csv文件中包含进去家族中，但是在合成.log文件中却是属于一个家族的。所以在finger not family[]中找出这个节点并放进去这个数组中。
            其中finger not family[finger,alleged_family]存放的也是一对多的情况
            '''
            if alleged_family != '' and alleged_family != 'null' and alleged_family != '[]':
                alleged_family = alleged_family.replace('\'', '')[1:-1].split(',')  # 字符串中的单引号（'）替换为空字符
                for i in range(len(alleged_family)):
                    alleged_family[i] = alleged_family[i].strip()  # 调用strip()方法去除两端的空格和其他空白字符（如换行符）
                if finger_not_family_dict.__contains__(finger):
                    old_v = finger_not_family_dict[finger]
                    old_v.extend(alleged_family)
                    finger_not_family_dict[finger] = old_v
                else:
                    v = []
                    v.extend(alleged_family)
                    finger_not_family_dict[finger] = v

            effective_family = row[5]
            if effective_family != '' and effective_family != 'null' and effective_family != '[]':
                effective_family = effective_family.replace('\'', '')[1:-1].split(',')
                for i in range(len(effective_family)):
                    effective_family[i] = effective_family[i].strip()
                if finger_effective_family_dict.__contains__(finger):
                    old_v = finger_effective_family_dict[finger]
                    old_v.extend(effective_family)
                    finger_effective_family_dict[finger] = old_v
                else:
                    v = []
                    v.extend(effective_family)
                    finger_effective_family_dict[finger] = v
                '''
                这上面的是将now_res.csv 文件中的effective_family统计出来，也是一对多的形式存放在finger_effective_family_dict[finger,effective_family]。
                下面的是g_onion、 g_onion_with_indirect 原本就是空的，现在加进去。g_all原本是micro得到g图的副本，现在进行添加，有进行添加。
                '''
                for i in range(len(effective_family) - 1):  # family字段不止一个，存在家族
                    g_onion.add_edge(effective_family[i], effective_family[i + 1])  # 纳入联通分量
                    g_onion_with_indirect.add_edge(effective_family[i], effective_family[i + 1])  # 纳入联通分量
                    g_all.add_edge(effective_family[i], effective_family[i + 1])  # 纳入联通分量

            indirect_family = row[6]
            if indirect_family != '' and indirect_family != 'null' and indirect_family != '[]':
                indirect_family = indirect_family.replace('\'', '')[1:-1].split(',')
                for i in range(len(indirect_family)):
                    indirect_family[i] = indirect_family[i].strip()
                if finger_indirect_family_dict.__contains__(finger):
                    old_v = finger_indirect_family_dict[finger]
                    old_v.extend(indirect_family)
                    finger_indirect_family_dict[finger] = old_v
                else:
                    v = []
                    v.extend(indirect_family)
                    finger_indirect_family_dict[finger] = v
                '''
                这上面的是将now_res.csv 文件中的indirect_family统计出来，也是一对多的形式存放在finger_indirect_family_dict[finger,indirect_family]。
                下面的是g_onion_with_indirect 、g_all进行补充添加。
                '''
                for i in range(len(indirect_family) - 1):  # family字段不止一个，存在家族
                    g_onion_with_indirect.add_edge(indirect_family[i], indirect_family[i + 1])  # 纳入联通分量
                    g_all.add_edge(indirect_family[i], indirect_family[i + 1])  # 纳入联通分量
            # nd = node(finger, asinfo, exit_policy, contact, alleged_family, effective_family, indirect_family)
            # node_list.append(nd)

    # 下面对其主要的节点进行处理：
    # if insert_contact_or_not:
    #     do_insert(val_contact, "contact")
    # if insert_as_or_not:
    #     do_insert(val_as, "as")
    # if insert_exitpolicy_or_not:
    #     do_insert(val_exitpolicy, "exit_policy")
    # if insert_micro_family_or_not:
    #     do_insert(row_val, "micro_family")

    # 空值保护
    val_ef = []
    if effective_family_or_not:
        g, val_ef = get_family(g=g, dict=finger_effective_family_dict)

    if micro_contact_family_or_not:
        g, val_res = get_family(g=g, dict=contact_finger_dict)

    #     do_insert(val, "contact_family")
    # if insert_onionoo_or_not:
    #     _, val = get_family(g=g_onion)  # _ 是一个占位符，用于表示我们对返回值的某部分不感兴趣。get_family 返回g,val,我们只关心元组中的第二个值（val），并且不需要处理第一个值。
    #     do_insert(val, "onionoo_family")
    # if insert_onionoo_indirect_or_not:
    #     _, val = get_family(g=g_onion_with_indirect)
    #     do_insert(val, "onionoo_indirect_family")
    # if insert_real_or_not:
    #     _, val = get_family(g_all, dict=contact_finger_dict)
    #     do_insert(val, "real_family")
    return g, val_ef, val_res, contact_finger_dict


def find_big_family(List):
    # 初始化
    len_list = 0
    num_list = 0
    count = 0
    for sub_list in List:
        if len(sub_list) > len_list:
            len_list = len(sub_list)
            num_list = count
        count += 1
    return len_list, num_list


def find_contact_in_details(Lists):
    with open("details.txt", "r") as file:
        data = json.load(file)
    # 获取 "relays" 列表
    relays = data.get("relays", [])
    for finger in Lists:
        for relay in relays:
            if "fingerprint" in relay and relay["fingerprint"] == finger[1:]:
                contact = relay.get("contact", "Contact not found")
                print(f"Contact for fingerprint {finger[1:]}: {contact}")


# 完成节点家族关系的分析和处理。
def process_contact_family(micro_path, res_csv, graph_pkl, detail_path, output_path):
    # 在process_micro_declared_family()中，就已经完成了依次根据micro信息来完成的连边
    # big_family_list 是列表，列表元素为家族列表，这里需要利用该列表找到最大的家族并且去查找他们的contact值。
    g, val, big_family_list = process_micro_declared_family(micro_path)
    family_len, num = find_big_family(big_family_list)
    print(f"family_len, num: {family_len, num}")  # big_family_list[num]为最大家族列表 然后 $finger 去查找匹配的contact值
    print(g)  # Graph with 5004 nodes and 4414 edges
    print(f"len(val): {len(val)}")  # 5004
    print("阶段一 OK，主要是完成micro文件下面内容的处理")
    import pickle
    with open(graph_pkl, 'wb') as f:
        pickle.dump(g, f)
    # 根据contact信息完成二次连边，contact信息节选自res.csv文件 res.csv目前的来源为：detials，
    """  
    选择effective_family_or_not=True，micro_contact_family_or_not=False，得到声明家族合集，选择双True得到声明家族与contact家族并集
    """
    g, val1, val2, contact_finger_dict = read_res_csv(g, res_csv, val,
                                                      effective_family_or_not=True,
                                                      micro_contact_family_or_not=True,
                                                      )
    print("阶段二 OK，将第一阶段得到的结果与now_res.csv文件进行匹配处理")
    contact_method(contact_finger_dict, val1, val2, detail_path, output_path)


def contact_method(contact_finger_dict, val1, val2, detail_path, output_path):
    val_clear = []
    for i in val1:
        val_clear.append(i[1])
    results = []

    count_hidden = 0
    count_public = 0
    for fanum, fingerprint in tqdm(val2, total=len(val2)):
        contact = ""
        or_addresses = ""
        if fingerprint not in val_clear:
            hidden_family = 1
            # print("*********************************")
            # print(f"隐藏家族节点为:{fingerprint} 它的关联家族为:{fanum}")
            count_hidden += 1
        else:
            hidden_family = 0
            count_public += 1
            # continue

        # for key, value in contact_finger_dict.items():
        #     if fingerprint in value:
        #         contact = key
        #         fingerlist = value

        with open(detail_path, 'r', encoding='utf-8') as f:
            relays = json.load(f)["relays"]
            for relay in relays:
                if relay.get("fingerprint") == fingerprint:
                    or_addresses = relay.get("or_addresses", "")
                    contact = relay.get("contact", "")
                    break

        results.append([or_addresses, fingerprint, contact, fanum, hidden_family])

    print(f"查询完成，共识别出{count_hidden}个隐藏家族节点, {count_public}个公开的家族节点")

    if results:
        with open(output_path + "method_1.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['or_addresses', 'fingerprint', 'contact', 'fanum', 'hidden_family'])  # 写入表头
            writer.writerows(results)  # 写入数据
        print(f"信息已保存至 {output_path}")
