from config import ROOT
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.family'] = 'SimHei'
picture_addr = f'{ROOT}//picture'


def draw_ip2finger(picture_addr,counts):
    """
    调用 compare_ip_and_finger("D:\\family_network\data\day.csv")
    :return:
    """
    n_values = range(1, 11)
    # plt.plot(n_values, counts, marker='o', color='b')
    plt.plot(n_values, counts, marker='o', color='b', label='改变指纹次数>=n的节点个数')

    # 为每个数据点添加数值标注
    for i, count in enumerate(counts):
        plt.text(n_values[i], count, str(count), ha='center', va='bottom', fontsize=9, color='red')


    plt.xlabel('改变指纹次数(n)')
    plt.ylabel('节点数量')
    plt.title('节点指纹变化次数图')
    plt.xticks(n_values)  # 设置 x 轴显示的刻度
    plt.grid(True)
    plt.legend()

    # 修改为你希望保存图像的路径
    plt.savefig(picture_addr)

    plt.show()
