import pickle
import sys

import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, ChebConv
import pandas as pd
import networkx as nx
from torch_geometric.utils import from_networkx
from config import ROOT
from method.MergeNet import merge_two_nets
from torch_geometric.data import data as D

def load_data(node_csv='E:\\family_network\\data\\node.csv'):
    df = pd.read_csv(node_csv)
    nodes = df['finger'].tolist()
    # 特征1:bandwidth更优的带宽高的
    # 特征2:delay更优的是时延低的
    # 特征3:variance更优的是方差小的
    # 特征4:Authority\BadExit\Exit\Fast\Guard\Stable\V2Dir\HSDir这几列为bool值，进行01联合编码作为第四特征
    bandwidth = df['bandwidth'].tolist()
    delay = df['delay_normalized'].tolist()
    variance = df['variance_normalized'].tolist()
    bool_cols = ['Authority', 'BadExit', 'Exit', 'Fast', 'Guard', 'Stable', 'V2Dir', 'HSDir']
    bool_features = df[bool_cols].astype(int).values.tolist()
    bandwidth = [(b - min(bandwidth)) / (max(bandwidth) - min(bandwidth)) for b in bandwidth]
    features = []
    for i in range(len(bandwidth)):
        feature = [bandwidth[i], delay[i], variance[i]] + bool_features[i]
        features.append(feature)
    labels = df['label'].tolist()

    avg_bandwidth = sum(bandwidth) / len(bandwidth)
    avg_delay = sum(delay) / len(delay)
    avg_variance = sum(variance) / len(variance)
    avg_bool_features = [0] * len(bool_cols)

    with open(f'{ROOT}\\pkl\\net.pkl', 'rb') as pkl_file:
        loaded_graph = pickle.load(pkl_file)

    with open(f'{ROOT}\\pkl\\net_circuit.pkl', 'rb') as pkl_file:
        loaded_graph_circuit = pickle.load(pkl_file)

    G = merge_two_nets(loaded_graph, loaded_graph_circuit, 0.5, 0.5)

    for node, feature, label in zip(nodes, features, labels):
        if node in G.nodes():
            G.nodes[node]['feature'] = feature
            G.nodes[node]['label'] = label

    for node in G.nodes():
        if 'feature' not in G.nodes[node]:
            G.nodes[node]['feature'] = [avg_bandwidth, avg_delay, avg_variance] + avg_bool_features
            G.nodes[node]['label'] = 0  # 假设未匹配节点的标签为 0，可根据需求修改

    # 从 networkx 图 G 中提取节点和边信息
    node_index_map = {node: i for i, node in enumerate(G.nodes())}
    edge_index = []
    edge_attr = []
    for u, v, data in G.edges(data=True):
        edge_index.append([node_index_map[u], node_index_map[v]])
        if 'weight' in data:
            edge_attr.append(data['weight'])
        else:
            edge_attr.append(1.0)

    # 将边信息转换为张量
    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    edge_attr = torch.tensor(edge_attr, dtype=torch.float)

    # 将节点特征转换为张量
    x = torch.tensor([G.nodes[node]['feature'] for node in G.nodes()], dtype=torch.float)
    y = torch.tensor([G.nodes[node]['label'] for node in G.nodes()], dtype=torch.long)

    # 创建训练、验证和测试的掩码
    num_nodes = len(G.nodes())
    train_mask = torch.ones(num_nodes, dtype=torch.bool)
    val_mask = torch.ones(num_nodes, dtype=torch.bool)
    test_mask = torch.ones(num_nodes, dtype=torch.bool)

    # 创建 torch_geometric 的 Data 对象
    data = D.Data(
        x=x,
        y=y,
        edge_index=edge_index,
        edge_attr=edge_attr,
        train_mask=train_mask,
        val_mask=val_mask,
        test_mask=test_mask
    )
    return data


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

class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = GCNConv(data.num_features, 16, cached=True,
                             normalize=True)
        #self.conv2 = GCNConv(16, data.num_classes, cached=True,
        self.conv2 = GCNConv(16, 2, cached=True,
                             normalize=True)
        # self.conv1 = ChebConv(data.num_features, 16, K=2)
        # self.conv2 = ChebConv(16, data.num_features, K=2)

    def forward(self):
        x, edge_index, edge_weight = data.x, data.edge_index, data.edge_attr
        x = F.relu(self.conv1(x, edge_index, edge_weight))
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index, edge_weight)
        return F.log_softmax(x, dim=1)






data = load_data()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model, data = Net().to(device), data.to(device)
optimizer = torch.optim.Adam([
    dict(params=model.conv1.parameters(), weight_decay=5e-4),
    dict(params=model.conv2.parameters(), weight_decay=0)
], lr=0.01)  # Only perform weight-decay on first convolution.

def train():
    model.train()
    optimizer.zero_grad()
    F.nll_loss(model()[data.train_mask], data.y[data.train_mask]).backward()
    #F.nll_loss(model()[data], data.y).backward()
    optimizer.step()


@torch.no_grad()
def test():
    model.eval()
    logits, accs = model(), []
    for _, mask in data('train_mask', 'val_mask', 'test_mask'):
        pred = logits[mask].max(1)[1]
        acc = pred.eq(data.y[mask]).sum().item() / mask.sum().item()
        accs.append(acc)
    return accs


best_val_acc = test_acc = 0
for epoch in range(1, 201):
    train()
    train_acc, val_acc, tmp_test_acc = test()
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        test_acc = tmp_test_acc
    log = 'Epoch: {:03d}, Train: {:.4f}, Val: {:.4f}, Test: {:.4f}'
    print(log.format(epoch, train_acc, best_val_acc, test_acc))


if __name__ == "__main__":
    data = load_data()
    print(data)

