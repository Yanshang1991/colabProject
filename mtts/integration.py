#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--total_info_path', type = str, help = '音频的汉字、拼音文件路径', default = "./workspace/txt/total_info.txt")
    parser.add_argument('-dr', '--duration_path', type = str, help = '时间文件路径', default = "./workspace/duration/duration.txt")
    parser.add_argument('-d', '--dst_path', type = str, help = '生成的最终文件路径', default = "./workspace/name_py_hz_dur.txt")
    args = parser.parse_args()

    total_info_path = args.total_info_path
    dst_path = args.dst_path
    duration_path = args.duration_path
    assert os.path.exists(total_info_path)
    assert os.path.exists(duration_path)

    with open(duration_path, "r", encoding = "utf-8") as d_f:
        d_lines = d_f.read().split("\n")
    duration_dir = {d_line.split("||")[0]: d_line.split("||")[1] for d_line in d_lines}

    with open(total_info_path, 'r', encoding = "utf-8") as f:
        lines = f.read().split("\n")

    result = []
    for line in lines:
        (name, hz, py, _, _) = line.split("|")
        duration = duration_dir[name]
        result.append(f"{name}|sil {py} sil|sil {hz} sil|{duration}")