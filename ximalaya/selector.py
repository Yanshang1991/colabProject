import csv
import os
import download_utils as du

# CSV文件路径，必填
csv_path = f"/content/colabProject/ximalaya/一禅575-714.csv"
# 下载目录
output_dir = f"/content/data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok = True)

# 解析url
url_list = []
with open(csv_path, 'r') as csv_file:
    reader = csv.reader(csv_file)
    for index, row in enumerate(reader):
        if index == 0:
            continue
        if row[2].startswith("20"):
            url = row[0]
            if url not in url_list:
                url_list.append(row[0])
# 多线程下载数据
du.many(url_list, f"/content/data", True)
