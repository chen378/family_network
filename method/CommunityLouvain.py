import torch
import networkx as nx
import community as community_louvain

# 构建图
G = nx.karate_club_graph()
num_nodes = G.number_of_nodes()

# 社区发现
partition = community_louvain.best_partition(G)

# 按社区划分节点
communities = {}
for node, community_id in partition.items():
    if community_id not in communities:
        communities[community_id] = []
    communities[community_id].append(node)

# 划分比例
train_ratio = 0.6
val_ratio = 0.2
test_ratio = 0.2

# 生成掩码
train_mask = torch.zeros(num_nodes, dtype=torch.bool)
val_mask = torch.zeros(num_nodes, dtype=torch.bool)
test_mask = torch.zeros(num_nodes, dtype=torch.bool)

for community_nodes in communities.values():
    community_size = len(community_nodes)
    train_size = int(community_size * train_ratio)
    val_size = int(community_size * val_ratio)

    train_nodes = community_nodes[:train_size]
    val_nodes = community_nodes[train_size:train_size + val_size]
    test_nodes = community_nodes[train_size + val_size:]

    train_mask[train_nodes] = True
    val_mask[val_nodes] = True
    test_mask[test_nodes] = True