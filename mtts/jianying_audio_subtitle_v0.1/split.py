#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
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
    duration = [get_one_duration(0, 0.3)]
    for word in words:
        start = float(word["start_time"]) / 1000
        end = float(word["end_time"]) / 1000
        duration.append(get_one_duration(start, end))
    duration.append(get_one_duration(0, 0.3))
    return duration


class DealThread(threading.Thread):
    def __init__(self, wav_path, json_info, result_list, wav_out_dir, dst_path):
        threading.Thread.__init__(self)
        self.wav_path = wav_path
        self.json_info = json_info
        self.result_list = result_list
        self.wav_out_dir = wav_out_dir
        self.dst_path = dst_path

    def run(self):
        print("开启线程：" + self.name)
        num_error = 0
        index = 0
        info_list = self.json_info["data"]["utterances"]
        last_info = None
        wav_audio = AudioSegment.from_mp3(self.wav_path).set_channels(1)  # 读取为拆分的音频
        tn = gp2py.TextNormal('gp.vocab', 'py.vocab', add_sp1 = True, fix_er = True)
        silent = AudioSegment.silent(150)  # 前后插入300毫秒静音
        for info in info_list:
            text = info["text"]  # 中文
            if last_info is not None:
                text = last_info["text"] + text

            if not is_all_chinese(text):
                num_error += 1
                print(f"内容：{text}，含有非中文字符。json文件：{self.name}，总数量：{num_error}")
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
            seg_audio = silent + wav_audio[start_time:end_time] + silent
            file_name = f"/{index}_{text}"
            seg_audio.export(os.path.join(self.wav_out_dir, file_name + ".wav"), format("wav"))
            words = info["words"]
            if last_info is not None:
                words = last_info["words"] + words
            duration_list = words_to_duration(words)
            duration_info = " ".join(duration_list) + "|0.0|" + str('%.2f' % (float(duration) / 1000))
            (py_list, gp_list) = tn.gp2py(text)
            self.result_list.append(f"{file_name}|{py_list[0]}|{gp_list[0]}|{duration_info}")
            last_info = None
            index += 1
        print("退出线程：" + self.name)
        with open(self.dst_path, "w", encoding = "utf-8") as txt_f:
            txt_f.write("\n".join(self.result_list))


def split(wav_path, json_info, wav_out_dir, dst_path):
    result_list = []
    deal_Thread = DealThread(wav_path, json_info, result_list = result_list, wav_out_dir = wav_out_dir, dst_path= dst_path)
    deal_Thread.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('-j', '--json_dir', type = str, help = 'json文件存放目录', default = "./workspace/json")
    # parser.add_argument('-w', '--wav_dir', type = str, help = '音频目录', default = "./workspace/wav")
    # parser.add_argument('-d', '--dst_path', type = str, help = '生成的最终文件路径', default = "./workspace/name_py_hz_dur.txt")
    # parser.add_argument('-o', '--wav_out_dir', type = str, help = '切分之后的音频目录', default = "./workspace/out")
    # parser.add_argument('-j', '--json_dir', type = str, help = 'json', default = ".")
    # parser.add_argument('-w', '--wav_dir', type = str, help = '音频目录', default = ".")
    parser.add_argument('-w', '--wav_path', type = str, help = '音频目录', default = "./out")
    parser.add_argument('-j', '--json_path', type = str, help = '生成的最终文件路径', default = "./name_py_hz_dur.txt")
    parser.add_argument('-d', '--dst_path', type = str, help = '生成的最终文件路径', default = "./name_py_hz_dur.txt")
    parser.add_argument('-o', '--wav_out', type = str, help = '生成的最终文件路径', default = "./name_py_hz_dur.txt")
    args = parser.parse_args()
    wav_path = args.wav_path
    dst_path = args.dst_path
    json_path = args.json_path
    wav_out = args.wav_out
    with open(json_path, 'r', encoding = "utf-8") as f:
        json_info = json.loads(f.read())
    split(wav_path, json_info, wav_out, dst_path)