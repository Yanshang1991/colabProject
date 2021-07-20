#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os

from pydub import AudioSegment

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src_dir', type = str, help = '要合并成一个wav文件的目录', default = "/Users/ZhangBo/Desktop/xima/儿童/test")
    parser.add_argument('-d', '--dst_dir', type = str, help = '输出合成wav文件的目录', default = "./workspace/wav")
    args = parser.parse_args()
    src_dir = args.src_dir
    assert os.path.exists(src_dir)
    dst_dir = args.dst_dir
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok = True)
    audio = AudioSegment.silent(300)
    index = 0
    for root, dirs, files in os.walk(src_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if not ext == ".wav":
                continue
            file_path = os.path.join(root, file)
            # new_file_path = root + "/" + name + ".pcm"
            # os.renames(file, new_file_path)
            audio += AudioSegment.from_file(file_path, sample_width = 2, frame_rate = 44100, channels = 2).set_channels(1)
            if audio.duration_seconds > 3600:  # 超过1个小时，保存
                audio.export(os.path.join(dst_dir, f"{index}.wav"), format = "wav")
                index += 1
                audio = AudioSegment.silent(300)
    if audio.duration_seconds > 3:
        audio.export(os.path.join(dst_dir, f"{index}.wav"), format = "wav")
