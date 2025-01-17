import networkx as nx

# 创建一个简单的图
G = nx.Graph()
G.add_edges_from([(1, 2, {'weight': 1}), (2, 3, {'weight': -1}), (3, 4, {'weight': 1})])

# 初始化节点标签，部分节点标签已知
labels = {1: 'good', 4: 'bad'}

# 标签传播
for _ in range(10):  # 迭代10次
    new_labels = {}
    for node in G.nodes():
        if node in labels:
            new_labels[node] = labels[node]
        else:
            neighbor_labels = {}
            for neighbor in G.neighbors(node):
                if neighbor in labels:
                    weight = G[node][neighbor]['weight']
                    if weight > 0:
                        label = labels[neighbor]
                    else:
                        label = 'good' if labels[neighbor] == 'bad' else 'bad'

                    if label not in neighbor_labels:
                        neighbor_labels[label] = 0
                    neighbor_labels[label] += abs(weight)
            if neighbor_labels:
                max_count = max(neighbor_labels.values())
                max_labels = [label for label, count in neighbor_labels.items() if count == max_count]
                new_labels[node] = max_labels[0]
    labels = new_labels

print(labels)