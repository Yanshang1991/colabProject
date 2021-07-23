#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os

from pydub import AudioSegment

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src_dir', type = str, help = '要合并成一个wav文件的目录', default = "/Users/ZhangBo/Desktop/xima/儿童/test")
    parser.add_argument('-d', '--dst_dir', type = str, help = '输出合成wav文件的目录', default = "./workspace/wav")
    parser.add_argument('-l', '--duration', type = int, help = '分块音频时长，单位：秒', default = "9000")
    args = parser.parse_args()
    duration = args.duration
    src_dir = args.src_dir
    assert os.path.exists(src_dir)
    dst_dir = args.dst_dir
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok = True)
    audio = None
    index = 0
    for root, dirs, files in os.walk(src_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if not ext == ".mp3":
                continue
            file_path = os.path.join(root, file)
            next = AudioSegment.from_mp3(file_path)
            if audio is None:
                audio = next
            else:
                audio += next
            if audio.duration_seconds > duration:  # 超过1个小时，保存
                audio.export(os.path.join(dst_dir, f"{index}.mp3"), format("mp3"))
                index += 1
                audio = None
    if audio.duration_seconds > 3:
        audio.export(os.path.join(dst_dir, f"{index}.mp3"), format("mp3"))