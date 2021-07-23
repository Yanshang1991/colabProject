#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import glob


def mv(src, tar_dir):
    shutil.move(src, tar_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src_dir', type = str, help = '要合并成一个wav文件的目录', default = "./raw")
    parser.add_argument('-d', '--dst_dir', type = str, help = '输出合成wav文件的目录', default = "./out")
    parser.add_argument('-l', '--limit', type = int, help = '每个文件夹音频个数', default = 30)
    args = parser.parse_args()
    limit = args.limit
    src_dir = args.src_dir
    assert os.path.exists(src_dir)
    dst_dir = args.dst_dir
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok = True)

    dir_index = 0
    index = 0
    for root, dirs, files in os.walk(src_dir, topdown = False, followlinks = True):
        for file in files:
            path = os.path.join(root, file)
            new_dir = os.path.join(dst_dir, str(dir_index))
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            new_path = os.path.join(new_dir, file)
            os.renames(path, new_path)
            index += 1
            if index >= limit:
                index = 0
                dir_index += 1
