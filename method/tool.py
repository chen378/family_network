from datetime import datetime
import calendar
import requests
import os
import tarfile
import json
import time
from requests.cookies import cookiejar_from_dict


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


def download_detail(download_path, url='https://onionoo.torproject.org/details', proxies=None):
    print(f"download_detail: {url}")
    response = requests.get(url, proxies=proxies)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"文件已成功下载到: {download_path}")
    else:
        print("下载失败，HTTP状态码:", response.status_code)
        return


# 通过指纹获得节点信息
# 最初是构造请求去访问Onionoo API，现在是直接从details.txt中进行搜索
def postfor_info(node, relays):
    finger = node.finger
    for relay in relays:
        if relay.get("fingerprint") == finger:
            # 如果找到了相应的 relay，更新 node 的信息
            node.asinfo = relay.get('as', 'null') if relay.get('as') is not None else 'null'
            node.exit_policy = relay.get('exit_policy', 'null') if relay.get('exit_policy') is not None else 'null'
            node.contact = relay.get('contact', 'null') if relay.get('contact') is not None else 'null'
            node.alleged_family = relay.get('alleged_family', 'null') if relay.get(
                'alleged_family') is not None else 'null'
            node.effective_family = relay.get('effective_family', 'null') if relay.get(
                'effective_family') is not None else 'null'
            node.indirect_family = relay.get('indirect_family', 'null') if relay.get(
                'indirect_family') is not None else 'null'
            return
    return


if __name__ == "__main__":
    year, month, _ = last_month()
    month_str = f"{month:02d}"
    url = f"https://collector.torproject.org/archive/relay-descriptors/microdescs/microdescs-{year}-{month}.tar.xz"
    descs_path = f"./downloads/{year}-{month}.tar.xz"
    detail_path = "./downloads/details.json"
    extract_to_folder = 'extracted_files'

    # 你需要代理才能访问这个网址
    proxies = {
        'http': 'http://127.0.0.1:10809',
        'https': 'http://127.0.0.1:10809',
    }

    download_microdescs(url, descs_path, extract_to_folder, proxies=proxies)
    download_detail(detail_path, proxies=proxies)
