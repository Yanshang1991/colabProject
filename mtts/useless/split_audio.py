#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
from pydub import AudioSegment

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wav_dir', type = str, help = '要切分的音频目录', default = "./workspace/wav")
    parser.add_argument('-t', '--txt_dir', type = str, help = 'txt字幕文件目录', default = "./workspace/txt")
    parser.add_argument('-d', '--dst_dir', type = str, help = '查分之后的音频和lab文件存放目录', default = "./workspace/data")
    args = parser.parse_args()
    wav_dir = args.wav_dir
    txt_dir = args.txt_dir
    dst_dir = args.dst_dir
    assert os.path.exists(wav_dir)
    assert os.path.exists(txt_dir)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok = True)

    silent = AudioSegment.silent(300)  # 前后插入300毫秒静音
    num = 0
    for root, dirs, files in os.walk(txt_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            # 过滤非txt文件
            if not ext == ".txt":
                continue
            txt_path = os.path.join(root, file)
            with open(txt_path, 'r') as content_f:
                lines = content_f.read().split("\n")
            wave_path = os.path.join(wav_dir, name + ".wav")
            wav_audio = AudioSegment.from_mp3(wave_path).set_channels(1)  # 读取为拆分的音频
            """
            根据字幕信息拆分音频
            """
            for line in lines:
                content = line.split("|")
                name = content[0]
                startM = int(content[3]) / 1000
                endM = startM + int(content[4]) / 1000
                audio_seg = wav_audio[startM:endM]
                with open(os.path.join(dst_dir, f"{name}.lab"), "w") as f:
                    f.write(content[2])
                (silent + audio_seg + silent).export(os.path.join(dst_dir, f"{name}.wav"), format("wav"))
                num += 1
    print(f"完成，总数：{num}")
