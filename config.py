import os


def set_project_root():
    # 获取当前脚本的绝对路径
    current_path = os.path.abspath(__file__)
    # 获取当前脚本所在的目录
    project_root = os.path.dirname(current_path)
    return project_root


# 保存项目根目录
ROOT = set_project_root()