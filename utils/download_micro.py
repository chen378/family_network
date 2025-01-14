import tarfile
from datetime import datetime
import calendar
import requests
import os
from config import ROOT
import utils.json_saver
def download_microdescs(url, download_path, extract_to_folder, proxies=None):
    print(f"download_microdescs: {url}")
    response = requests.get(url, proxies=proxies)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"文件已成功下载到: {download_path}")
    else:
        print("下载失败，HTTP状态码:", response.status_code)
        return

    if not os.path.exists(extract_to_folder):
        os.makedirs(extract_to_folder)

    with tarfile.open(download_path, 'r:xz') as tar_ref:
        tar_ref.extractall(extract_to_folder)
        print(f"文件已解压到: {extract_to_folder}")


def last_month():
    current_date = datetime.now()

    if current_date.month == 1:
        previous_month = 12
        previous_year = current_date.year - 1
    else:
        previous_month = current_date.month - 1
        previous_year = current_date.year

    # 获取上个月的天数
    _, days_in_previous_month = calendar.monthrange(previous_year, previous_month)

    return previous_year, previous_month, days_in_previous_month


def MicroDownload(descs_path, extract_to_folder):

    """
    :param descs_path: micro压缩文件下载地址
    :param extract_to_folder: micro压缩文件解压地址
    :return: 下载并解压micro,如果extract_to_folder存在，则不操作，无返回值
    """

    if os.path.exists(descs_path):
        print(f"The folder {descs_path} already exists, no operation will be performed.")
        return

    year, month, day = last_month()
    month_str = f"{month:02d}"
    url = f"https://collector.torproject.org/archive/relay-descriptors/microdescs/microdescs-{year}-{month_str}.tar.xz"
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }
    download_microdescs(url, descs_path, extract_to_folder, proxies=proxies)


if __name__ == "__main__":

    MicroDownload(descs_path, extract_to_folder)
