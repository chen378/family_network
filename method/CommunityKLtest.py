import sys

import networkx as nx
from networkx.algorithms.community import kernighan_lin_bisection
import matplotlib.pyplot as plt
from config import ROOT
import pickle

from method.CircuitAnlysis import save_node_neighbors_to_txt

# 创建一个简单的图
# G = nx.Graph()
# G.add_edges_from([(1, 2), (1, 3), (2, 3), (4, 5), (4, 6), (5, 6)])
# G.add_node(7)
# # 使用 Kernighan-Lin 算法进行图划分
# partition = kernighan_lin_bisection(G)
#
# # 输出划分结果
# print(partition)

with open(f'{ROOT}\\pkl\\net.pkl', 'rb') as pkl_file:
    loaded_graph = pickle.load(pkl_file)
# save_node_neighbors_to_txt(loaded_graph,'g_family.txt')
print(loaded_graph.number_of_nodes())

with open(f'{ROOT}\\pkl\\net_circuit.pkl', 'rb') as pkl_file:
    loaded_graph_circuit = pickle.load(pkl_file)
print(loaded_graph_circuit.number_of_nodes())
sys.exit()

# nx.draw(loaded_graph)
# plt.show()
# plt.show(loaded_graph_circuit)

partition = kernighan_lin_bisection(loaded_graph_circuit)
# 输出划分结果
print(len(list(partition)))
print(len(list(partition)[0]))
print(len(list(partition)[1]))

# def draw_spring(G, com):
#      pos = nx.spring_layout(G)  # 节点的布局为spring型
#      NodeId = list(G.nodes())
#      node_size = [G.degree(i) ** 1.2 * 90 for i in NodeId]  # 节点大小
#      plt.figure(figsize=(8, 6))  # 图片大小
#      nx.draw(G, pos, with_labels=True, node_size=node_size, node_color='w', node_shape='.')
#      color_list = ['pink', 'orange', 'r', 'g', 'b', 'y', 'm', 'gray', 'black', 'c', 'brown']
#      for i in range(len(com)):
#          nx.draw_networkx_nodes(G, pos, nodelist=com[i], node_color=color_list[i])
#      plt.show()
#
# import matplotlib.pyplot as plt
# G = nx.karate_club_graph()
# com = list(kernighan_lin_bisection(G))
#
#
# com = list(kernighan_lin_bisection(G))
# print('社区数量', len(com))
# draw_spring(G, com)
