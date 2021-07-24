#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import time
from utils import time_utils as tu
import glob
import os
start = time.time()
# -----------要移动的目录或者文件-----------
src = r"/content/drive/MyDrive/Dataset/label/audio"

# -----------要移动的文件类型-----------
f_type = ""

# -----------目标目录名称-----------
dst_dir = r"/content/"

if os.path.isdir(src):
    files = glob.glob(os.path.join(src, "*" + f_type))
    for file in files:
        (dir, f_name) = os.path.split(file)
        os.rename(file, os.path.join(dst_dir, f_name))
else:
    (dir, f_name) = os.path.split(src)
    os.rename(src, os.path.join(dst_dir, f_name))


glob.glob(os.path.join(src))

def add(index):
    index += 1


if __name__ == '__main__':
    print(os.path.split("asdada/asdasdsa/asda.aaa"))


    # print(int("_86967_爸爸我长大了要当一名北极探险家".split("_")[1]) > 0)
    # with open("aaa.json", 'r', encoding = "utf-8") as f:
    #     json_info = json.load(f)
    # with open("51.json", "w") as w_f:
    #     json.dump(json_info, w_f)
    # infos = json_info["data"]["utterances"]
    # index = 0
    # for infos in infos:
    #     index += 1  # for root, dirs, files in os.walk("/content/wav/", topdown = False, followlinks = True):  #     for file in files:  #         (name, ext) = os.path.splitext(file)  #         if ext == ".wav":  #             if not os.path.exists(os.path.join(root, name + ".json")):  #                 os.rename(os.path.join(root, file), os.path.join("/content/wav_2", file))
    # print(index)
