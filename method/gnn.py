import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, ChebConv  # noqa
from torch_geometric.data import Data

# 参数设置
num_node_features = 10
hidden_channels = 16
num_classes = 2
num_time_steps = 5

# 数据准备
edge_index = torch.tensor([[1, 2, 3], [0, 0, 0]], dtype=torch.long)  # 2 x E
x = torch.tensor([[1], [3], [4], [5]], dtype=torch.float)  # N x emb(in)
edge_attr = torch.tensor([10, 20, 30], dtype=torch.float)  # E x edge_dim
y = torch.tensor([1, 0, 0, 1])
train_mask = torch.tensor([True, True, True, True], dtype=torch.bool)
val_mask = train_mask
test_mask = train_mask

data = Data()
data.x, data.y, data.edge_index, data.edge_attr, data.train_mask, data.val_mask, data.test_mask \
    = x, y, edge_index, edge_attr, train_mask, val_mask, test_mask

# 模型定义
class Net(torch.nn.Module):
    def __init__(self, num_node_features, hidden_channels, num_classes):
        super(Net, self).__init__()
        self.conv1 = GCNConv(num_node_features, hidden_channels, cached=True,
                             normalize=True)
        # self.conv2 = GCNConv(16, data.num_classes, cached=True,
        self.conv2 = GCNConv(hidden_channels, num_classes, cached=True,
                             normalize=True)
        # self.conv1 = ChebConv(data.num_features, 16, K=2)
        # self.conv2 = ChebConv(16, data.num_features, K=2)

    def forward(self, x, edge_index, edge_weight):
        x = F.relu(self.conv1(x, edge_index, edge_weight))
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index, edge_weight)
        return F.log_softmax(x, dim=1)

# 训练配置
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Net(num_node_features, hidden_channels, num_classes).to(device)
data = data.to(device)
optimizer = torch.optim.Adam([
    dict(params=model.conv1.parameters(), weight_decay=5e-4),
    dict(params=model.conv2.parameters(), weight_decay=0)
], lr=0.01)  # Only perform weight-decay on first convolution.

# 训练和测试函数
def train():
    model.train()
    optimizer.zero_grad()
    F.nll_loss(model(data.x, data.edge_index, data.edge_attr)[data.train_mask], data.y[data.train_mask]).backward()
    optimizer.step()
    return model

def test(model):
    model.eval()
    logits, accs = model(data.x, data.edge_index, data.edge_attr), []
    for _, mask in data('train_mask', 'val_mask', 'test_mask'):
        pred = logits[mask].max(1)[1]
        acc = pred.eq(data.y[mask]).sum().item() / mask.sum().item()
        accs.append(acc)
    return accs

# 训练过程
best_val_acc = test_acc = 0
for epoch in range(1, 201):
    model = train()
    train_acc, val_acc, tmp_test_acc = test(model)
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        test_acc = tmp_test_acc
    log = 'Epoch: {:03d}, Train: {:.4f}, Val: {:.4f}, Test: {:.4f}'
    print(log.format(epoch, train_acc, best_val_acc, test_acc))