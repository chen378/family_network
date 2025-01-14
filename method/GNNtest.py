import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric_temporal.nn.recurrent import A3TGCN2


class TimeSliceGNN(nn.Module):
    def __init__(self, num_node_features, hidden_channels, num_classes, num_time_steps):
        super(TimeSliceGNN, self).__init__()
        # 图卷积层
        self.gcn1 = GCNConv(num_node_features, hidden_channels)
        self.gcn2 = GCNConv(hidden_channels, hidden_channels)
        # 时间序列处理层
        self.temporal_layer = A3TGCN2(in_channels=hidden_channels, out_channels=hidden_channels, periods=num_time_steps)
        # 输出层
        self.fc = nn.Linear(hidden_channels, num_classes)

    def forward(self, data_list):
        # data_list是一个包含多个时间切片数据的列表，每个元素是一个图数据对象
        all_outputs = []
        for data in data_list:
            x, edge_index = data.x, data.edge_index
            # 第一层图卷积
            x = self.gcn1(x, edge_index)
            x = F.relu(x)
            # 第二层图卷积
            x = self.gcn2(x, edge_index)
            x = F.relu(x)
            all_outputs.append(x)
        # 将不同时间切片的输出堆叠
        x = torch.stack(all_outputs)
        # 时间序列处理
        x = self.temporal_layer(x)
        # 取最后一个时间步的输出
        x = x[-1]
        # 全连接层输出
        x = self.fc(x)
        return F.log_softmax(x, dim=1)


# 示例参数
num_node_features = 10  # 节点特征的维度
hidden_channels = 16  # 隐藏层维度
num_classes = 2  # 分类的类别数（例如正常节点和风险节点）
num_time_steps = 5  # 时间切片的数量


# 初始化模型
model = TimeSliceGNN(num_node_features, hidden_channels, num_classes, num_time_steps)


# 示例输入数据，这里假设 data_list 是一个包含多个时间切片的图数据列表，每个元素是一个 torch_geometric.data.Data 对象
data_list = []
# 示例：添加一些数据
for i in range(num_time_steps):
    x = torch.randn(100, num_node_features)  # 假设每个时间片有 100 个节点
    edge_index = torch.randint(0, 100, (2, 200))  # 假设每个时间片有 200 条边
    data = Data(x=x, edge_index=edge_index)
    data_list.append(data)


# 定义优化器和损失函数
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()


# 训练过程
def train():
    model.train()
    optimizer.zero_grad()
    out = model(data_list)
    # 假设 labels 是节点的真实标签
    labels = torch.randint(0, num_classes, (100,))
    loss = criterion(out, labels)
    loss.backward()
    optimizer.proceed()
    return loss.item()


# 测试过程
def test():
    model.eval()
    out = model(data_list)
    # 假设 labels 是节点的真实标签
    labels = torch.randint(0, num_classes, (100,))
    pred = out.argmax(dim=1)
    correct = pred.eq(labels).sum().item()
    acc = correct / len(labels)
    return acc