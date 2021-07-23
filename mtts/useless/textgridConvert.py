#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import textgrid
import numpy as np


def get_one_duration(start, end, sample_rate, hop_length):
    return str(np.round(end * sample_rate / hop_length) - np.round(start * sample_rate / hop_length))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src', type = str, help = 'textGrid文件所在目录', default = "./workspace/internal")
    parser.add_argument('-d', '--dst_dir', type = str, help = '生成的duration文件所在目录', default = "./workspace/duration")
    # parser.add_argument('-d', '--dst_dir', type = str, help = '生成的duration文件所在目录', default = ".")
    # parser.add_argument('-s', '--src', type = str, help = 'textGrid文件所在目录', default = ".")
    parser.add_argument('-r', '--sample_rate', type = int, help = '音频文件采样率', default = "44100")
    args = parser.parse_args()
    src = args.src
    dst_dir = args.dst_dir
    sample_rate = args.sample_rate
    assert os.path.exists(src)
    if os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok = True)

    tg = textgrid.TextGrid()
    lines = []
    for root, dirs, files in os.walk(src, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if not ext == ".TextGrid":
                continue
            path = os.path.join(root, file)
            tg.read(path)
            duration = []
            for interval in tg.tiers[0]:
                duration.append(get_one_duration(interval.minTime, interval.maxTime, sample_rate / 2, 256))
            durations = " ".join(duration)
            lines.append(f"{name}||{durations}|0.0|{'%.2f'%tg.maxTime}")
    with open(os.path.join(dst_dir, "duration.txt"), "w", encoding = "utf-8") as d_f:
        d_f.write("\n".join(lines))
