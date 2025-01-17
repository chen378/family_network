# 这是一个示例 Python 脚本。
import os
from config import ROOT
from utils.download_micro import MicroDownload,last_month

year, month, day = last_month()
month_str = f"{month:02d}"
descs_path = f"./download/{year}-{month_str}.tar.xz"
extract_to_folder = f"./download"

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':

    # 下载数据
    MicroDownload(descs_path, extract_to_folder)


    # 数据处理


    # 数据合并


    # 生成图

    # 图神经网络