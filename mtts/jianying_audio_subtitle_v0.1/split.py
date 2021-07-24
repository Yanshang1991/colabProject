#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import glob
import os
import json
import threading

from pydub import AudioSegment
from pypinyin import pinyin, Style
import numpy as np

import gp2py


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
    duration = [get_one_duration(0, 0.15)]
    for word in words:
        start = float(word["start_time"]) / 1000
        end = float(word["end_time"]) / 1000
        duration.append(get_one_duration(start, end))
    duration.append(get_one_duration(0, 0.15))
    return duration


def deal(wav_path, json_info, wav_out_dir, result_list, dst_path, wav_name = "", index = 0, split_audio = True):
    num_error = 0
    info_list = json_info["data"]["utterances"]
    last_info = None
    if split_audio:
        wav_audio = AudioSegment.from_mp3(wav_path).set_channels(1)  # 读取为拆分的音频
    tn = gp2py.TextNormal('gp.vocab', 'py.vocab', add_sp1 = True, fix_er = True)
    silent = AudioSegment.silent(150)  # 前后插入300毫秒静音
    for info in info_list:
        text = info["text"]  # 中文
        if last_info is not None:
            text = last_info["text"] + text

        if not is_all_chinese(text):
            num_error += 1
            print(f"内容：{text}，含有非中文字符。总数量：{num_error}")
            continue
        end_time = info["end_time"]
        if last_info is not None:
            start_time = last_info["start_time"]
        else:
            start_time = info["start_time"]
        duration = end_time - start_time  # 持续时间
        # 如果该片段的时间小于2秒，合并到下一个片段中
        if duration < 1 and last_info is None:
            last_info = info
            continue
        file_name = f"{wav_name}_{index}_{text}"
        if split_audio:
            seg_audio = silent + wav_audio[start_time:end_time] + silent
            seg_audio.export(os.path.join(wav_out_dir, file_name + ".wav"), format("wav"))
        words = info["words"]
        if last_info is not None:
            words = last_info["words"] + words
        duration_list = words_to_duration(words)
        duration_info = " ".join(duration_list) + "|0.0|" + str('%.2f' % (float(duration) / 1000))
        (py_list, gp_list) = tn.gp2py(text)
        result_list.append(f"{file_name}|{py_list[0]}|{gp_list[0]}|{duration_info}")
        last_info = None
        index += 1
    with open(dst_path, "w", encoding = "utf-8") as txt_f:
        txt_f.write("\n".join(result_list))
    return index


class DealThread(threading.Thread):
    def __init__(self, wav_path, json_info, result_list, wav_out_dir, dst_path, wav_name):
        threading.Thread.__init__(self)
        self.wav_path = wav_path
        self.json_info = json_info
        self.result_list = result_list
        self.wav_out_dir = wav_out_dir
        self.dst_path = dst_path
        self.wav_name = wav_name

    def run(self):
        deal(wav_path = self.wav_path, json_info = self.json_info, wav_out_dir = self.wav_out_dir, result_list = self.result_list, dst_path = self.dst_path, wav_name = self.wav_name)


def split_(wav_path, json_info, wav_out_dir, dst_path, wav_name):
    result_list = []
    deal_thread = DealThread(wav_path, json_info, result_list = result_list, wav_out_dir = wav_out_dir, dst_path = dst_path, wav_name = wav_name)
    deal_thread.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json_dir', type = str, help = 'json文件存放目录', default = "./workspace/json")
    parser.add_argument('-w', '--input_wav_dir', type = str, help = '音频目录', default = "./workspace/wav")
    parser.add_argument('-d', '--dst_path', type = str, help = '生成的最终文件路径', default = "./workspace/name_py_hz_dur.txt")
    parser.add_argument('-o', '--out_wav_dir', type = str, help = '切分之后的音频目录', default = "./workspace/out")
    parser.add_argument('-t', '--input_wav_type', type = str, help = '输入音频的类型', default = ".mp3")
    parser.add_argument('-p', '--split_audio', type = bool, help = '是否切分音频', default = True)
    args = parser.parse_args()
    input_wav_dir = args.input_wav_dir
    json_dir = args.json_dir
    dst_path = args.dst_path
    out_wav_dir = args.out_wav_dir
    input_wav_type = args.input_wav_type
    split_audio = args.split_audio
    result_list = []
    index = 0
    if not os.path.exists(out_wav_dir):
        os.makedirs(out_wav_dir)

    for root, dirs, files in os.walk(json_dir, topdown = False, followlinks = True):
        for file in files:
            (name, ext) = os.path.splitext(file)
            if not ext == ".json":
                continue
            print(f"开始处理，文件{file}")
            wav_path = os.path.join(input_wav_dir, name + input_wav_type)
            if not os.path.exists(wav_path):
                print(f"音频文件：{wav_path}，不存在")
                continue

            try:
                with open(os.path.join(root, file), 'r') as f:
                    json_info = json.load(f)
            except:
                print(f"json文件：{file}，读取失败")
                continue
            index = deal(wav_path = wav_path, json_info = json_info, wav_out_dir = out_wav_dir, result_list = result_list, dst_path = dst_path, index = index, split_audio = True)
            print(f"处理完成，总数：{index}")
    with open(dst_path, "w", encoding = "utf-8") as txt_f:
        txt_f.write("\n".join(result_list))
