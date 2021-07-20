#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import json

from pydub import AudioSegment
from pypinyin import pinyin, Style
import numpy as np


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


def get_pin_yin(s):
    pinyinlist = pinyin(s, Style.TONE3)

    def handle(ll):
        if (is_number(ll[0][-1]) or ll[0] == ' '):
            return ll[0]
        return ll[0] + '5'

    py = list(map(handle, pinyinlist))
    py = ' '.join(py)
    return py


# 检验是否全是中文字符
def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True


def get_one_duration(start, end, sample_rate = 22050, hop_length = 256):
    return str(int(np.round(end * sample_rate / hop_length) - np.round(start * sample_rate / hop_length)))


def words_to_duration(words):
    duration = [get_one_duration(0, 0.3)]
    for word in words:
        start = float(word["start_time"]) / 1000
        end = float(word["end_time"]) / 1000
        duration.append(get_one_duration(start, end))
    duration.append(get_one_duration(0, 0.3))
    return duration


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json_dir', type = str, help = 'json文件存放目录', default = "./workspace/json")
    parser.add_argument('-w', '--wav_dir', type = str, help = '音频目录', default = "./workspace/wav")
    parser.add_argument('-d', '--dst_path', type = str, help = '生成的最终文件路径', default = "./workspace/name_py_hz_dur.txt")
    parser.add_argument('-o', '--wav_out_dir', type = str, help = '切分之后的音频目录', default = "./workspace/out")
    # parser.add_argument('-j', '--json_dir', type = str, help = 'json', default = ".")
    # parser.add_argument('-w', '--wav_dir', type = str, help = '音频目录', default = ".")
    # parser.add_argument('-o', '--wav_out_dir', type = str, help = '音频目录', default = "./out")
    # parser.add_argument('-d', '--dst_path', type = str, help = '生成的最终文件路径', default = "./name_py_hz_dur.txt")
    args = parser.parse_args()
    json_dir = args.json_dir
    wav_dir = args.wav_dir
    dst_path = args.dst_path
    wav_out_dir = args.wav_out_dir

    result = []
    index = 0  # 文件的名称
    num_error = 0
    silent = AudioSegment.silent(300)  # 前后插入300毫秒静音
    for root, dirs, files in os.walk(json_dir, topdown = False, followlinks = True):
        for file in files:
            (name, ext) = os.path.splitext(file)
            if not ext == ".json":
                continue
            with open(os.path.join(root, file), 'r', encoding = 'utf-8') as json_f:  # json文件
                draft = json.load(json_f)
            info_list = draft["data"]["utterances"]
            for info in info_list:
                text = info["text"]  # 中文
                if not is_all_chinese(text):
                    num_error += 1
                    print(f"内容：{text}，含有非中文字符。总数量：{num_error}")
                    continue

                duration = info["end_time"] - info["start_time"]  # 持续时间
                wav_path = os.path.join(wav_dir, name + ".wav")  # 音频文件路径
                wav_audio = AudioSegment.from_mp3(wav_path).set_channels(1)  # 读取为拆分的音频
                seg_audio = silent + wav_audio[info["start_time"]:info["end_time"]] + silent
                # seg_audio.export(os.path.join(wav_out_dir, f"text{index}.wav"), format("wav"))
                seg_audio.export(wav_out_dir + f"/text{index}.wav", format("wav"))
                duration_list = words_to_duration(info["words"])
                duration_info = " ".join(duration_list) + "|0.0|" + str('%.2f' % (float(duration) / 1000))
                result.append(f"text{index}|sil {get_pin_yin(text)} sil|sil {text} sil|{duration_info}")
                index += 1
    with open(dst_path, "w", encoding = "utf-8") as txt_f:
        txt_f.write("\n".join(result))
