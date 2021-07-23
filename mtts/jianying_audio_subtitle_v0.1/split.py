#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import json
import threading

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


class DealThread(threading.Thread):
    def __init__(self, wav_path, json_path, result_list, wav_out_dir):
        threading.Thread.__init__(self)
        self.wav_path = wav_path
        self.json_path = json_path
        self.result_list = result_list
        self.wav_out_dir = wav_out_dir

    def run(self):
        print("开启线程：" + self.name)
        num_error = 0
        index = 0
        with open(self.json_path, 'r', encoding = 'utf-8') as json_f:  # json文件
            draft = json.load(json_f)
        info_list = draft["data"]["utterances"]
        for info in info_list:
            text = info["text"]  # 中文
            if not is_all_chinese(text):
                num_error += 1
                print(f"内容：{text}，含有非中文字符。json文件：{self.name}，总数量：{num_error}")
                continue
            duration = info["end_time"] - info["start_time"]  # 持续时间
            wav_audio = AudioSegment.from_mp3(self.wav_path).set_channels(1)  # 读取为拆分的音频
            seg_audio = silent + wav_audio[info["start_time"]:info["end_time"]] + silent
            file_name = f"/text{self.name}-{index}.wav"
            seg_audio.export(self.wav_out_dir + file_name, format("wav"))
            duration_list = words_to_duration(info["words"])
            duration_info = " ".join(duration_list) + "|0.0|" + str('%.2f' % (float(duration) / 1000))
            new_text = " ".join(text)
            self.result_list.append(f"text{self.name}-{index}|sil {get_pin_yin(text)} sil|sil {new_text} sil|{duration_info}")
            index += 1
        print("退出线程：" + self.name)
        with open(dst_path, "w", encoding = "utf-8") as txt_f:
            txt_f.write("\n".join(result))


def split(wav_path, json_info):
    result_list = []
    DealThread(path = os.path.join(root, file), json_name = name, result_list = result, wav_out_dir = wav_out_dir)


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
    if os.path.exists(wav_out_dir):
        os.makedirs(wav_out_dir, exist_ok = True)

    result = []
    index = 0  # 文件的名称
    num_error = 0
    silent = AudioSegment.silent(150)  # 前后插入300毫秒静音
    threads = []
    for root, dirs, files in os.walk(json_dir, topdown = False, followlinks = True):
        for file in files:
            (name, ext) = os.path.splitext(file)
            if not ext == ".json":
                continue
            thread = DealThread(path = os.path.join(root, file), json_name = name, result_list = result, wav_out_dir = wav_out_dir)
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()  # with open(dst_path, "w", encoding = "utf-8") as txt_f:  #     txt_f.write("\n".join(result))
