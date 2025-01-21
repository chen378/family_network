import networkx as nx

def merge_two_nets(g1, g2, weight1, weight2):
    """
    将两个图融合成一个新图，并根据给定的权重调整边的权重。

    参数:
    g1 (networkx.Graph): 第一个图
    g2 (networkx.Graph): 第二个图
    weight1 (float): 第一个图的边权重系数
    weight2 (float): 第二个图的边权重系数

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

    # 依次添加两个图到新图中
    add_graph_to_total(g1, weight1)
    add_graph_to_total(g2, weight2)

    return g_total


if __name__ == "__main__":
    merge_two_nets()