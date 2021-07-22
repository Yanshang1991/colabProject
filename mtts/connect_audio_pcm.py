#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os

from pydub import AudioSegment

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src_dir', type = str, help = '要合并成一个wav文件的目录', default = "/Users/ZhangBo/Desktop/xima/儿童/test")
    parser.add_argument('-d', '--dst_dir', type = str, help = '输出合成wav文件的目录', default = "./workspace/wav")
    parser.add_argument('-a', '--silent', type = int, help = '音频前后的静音时长', default = "150")
    parser.add_argument('-l', '--duration', type = int, help = '分块音频时长，单位：秒', default = "9000")
    args = parser.parse_args()
    silent = args.silent
    src_dir = args.src_dir
    duration = args.duration
    assert os.path.exists(src_dir)
    dst_dir = args.dst_dir
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok = True)
    audio = AudioSegment.silent(silent)
    index = 0
    for root, dirs, files in os.walk(src_dir, topdown = False, followlinks = True):
        for file in files:
            try:
                name, ext = os.path.splitext(file)
                file_path = os.path.join(root, file)
                # new_file_path = root + "/" + name + ".pcm"
                # os.renames(file, new_file_path)
                audio += AudioSegment.from_file(file_path, sample_width = 2, frame_rate = 44100, channels = 2)
                if audio.duration_seconds > duration:  # 超过指定时长，保存
                    print(f"保存第{index}个音频文件")
                    audio.export(os.path.join(dst_dir, f"{index}.mp3"), format = "raw")
                    index += 1
                    audio = AudioSegment.silent(silent)
            except:
                print(f"异常")
                continue
    if audio.duration_seconds > 3:
        audio.export(os.path.join(dst_dir, f"{index}.mp3"), format = "raw")
