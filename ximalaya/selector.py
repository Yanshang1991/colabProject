import csv
from typing import List

import download_utils as du


def read_from_csv(csv_path: str) -> List:
    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
    return reader


if __name__ == '__main__':



    path = f"./一禅575-714.csv"
    # row_list = read_from_csv(path)
    url_list = []
    with open(path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for index, row in enumerate(reader):
            if index == 0:
                continue
            if row[2].startswith("20"):
                url = row[0]
                if url not in url_list:
                    url_list.append(row[0])
    index = 84
    for url in url_list:
        du.single(url, f"./data", str(index) + ".m4a")
        index += 1
