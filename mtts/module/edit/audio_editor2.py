#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import glob
import time
from concurrent.futures import ThreadPoolExecutor

from pydub import AudioSegment

import gp2py
import numpy as np
from audio_info import AudioInfo


def _is_all_chinese(input_text):
    # 检验是否全是中文字符
    for _char in input_text:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True


def _get_one_duration(start, end, sample_rate = 22050, hop_length = 256):
    return str(int(np.round(end * sample_rate / hop_length) - np.round(start * sample_rate / hop_length)))


def _words_to_duration(words):
    duration = [_get_one_duration(0, 0.15)]
    for word in words:
        start = float(word["start_time"]) / 1000
        end = float(word["end_time"]) / 1000
        duration.append(_get_one_duration(start, end))
    duration.append(_get_one_duration(0, 0.15))
    return duration


class AudioEditor:
    def __init__(self, config, workspace_path, pool: ThreadPoolExecutor, all_tasks: list):
        self.config = config
        self.workspace_path = workspace_path
        self.pool = pool
        self.all_tasks = all_tasks
        self.jointed_audio_dir = os.path.join(self.workspace_path, "jointed")
        self.jointed_audio_type = self.config["jointed_audio_type"]
        if not os.path.exists(self.jointed_audio_dir):
            os.makedirs(self.jointed_audio_dir, exist_ok = True)
        self.cut_audio_type = self.config["cut_audio_type"]
        self.cut_audio_dir = os.path.join(self.workspace_path, "cut")
        if not os.path.exists(self.cut_audio_dir):
            os.makedirs(self.cut_audio_dir, exist_ok = True)

    def joint_audio_by_info(self, audio_info: AudioInfo, recognize_action):
        tar_audio = None
        for sub_audio_info in audio_info.sub_audio_info_list:
            if tar_audio is None:
                tar_audio = AudioSegment.from_file(sub_audio_info.path)
            else:
                tar_audio += AudioSegment.from_file(sub_audio_info.path)

        def export_action():
            print(f"开始写入合成的音频文件: {audio_info.path}")
            start_time = time.time()
            tar_audio.export(audio_info.path, format(self.jointed_audio_type.split(".")[-1]))
            audio_info.joint_complete = True
            print(f"success------文件：{audio_info.path}写入成功，时长：{audio_info.duration_seconds}秒，写入耗时：{str(time.time() - start_time)}")
            print(f"{audio_info.path}，调用识别回调")
            recognize_action(audio_info)

        self.all_tasks.append(self.pool.submit(export_action))

    def joint_audio(self, raw_audio_dir: str, recognize_action, raw_audio_type: str = None):
        """
        拼接音频
        :param raw_audio_dir: 音频文件所在目录
        :param recognize_action: 音频转换完成，回调该方法，开始识别音频
        :param raw_audio_type: 输入音频类型，不传默认读取文件下所有的文件
        :return: 音频信息列表
        """
        # 参数校验
        assert os.path.exists(raw_audio_dir)
        tar_audio = None

        # 获取音频文件
        file_match_path = os.path.join(raw_audio_dir, "*")
        if raw_audio_type is not None:
            file_match_path += raw_audio_type
        files = glob.glob(file_match_path)
        small_audio_info_list = [AudioInfo(path = f) for f in files]
        audio_info_list = []
        # 文件序号
        index = 0
        limit = self.config["jointed_audio_limit"]
        one_jointed_audio_info_list = []  # 一个合成音频的子音频信息，主要为了记录路径信息

        def export_action(cur_index, cur_tar_audio, cur_one_jointed_audio_info_list: list):
            tar_audio_path = os.path.join(self.jointed_audio_dir, str(cur_index).zfill(8) + self.jointed_audio_type)
            audio_info = AudioInfo(path = tar_audio_path, duration_seconds = cur_tar_audio.duration_seconds, sub_audio_info_list = cur_one_jointed_audio_info_list, id = cur_index)
            audio_info_list.append(audio_info)
            print(f"开始写入合成的音频文件: {tar_audio_path}")
            start_time = time.time()
            cur_tar_audio.export(tar_audio_path, format(self.jointed_audio_type.split(".")[-1]))
            audio_info.joint_complete = True
            print(f"success------文件：{audio_info.path}写入成功，时长：{audio_info.duration_seconds}秒，写入耗时：{str(time.time() - start_time)}")
            print(f"{audio_info.path}，调用识别回调")
            recognize_action(audio_info)

        for small_audio_info in small_audio_info_list:
            print(small_audio_info.path)
            audio = AudioSegment.from_file(small_audio_info.path)
            small_audio_info.duration_seconds = audio.duration_seconds
            if tar_audio is None:
                tar_audio = audio
            else:
                tar_audio += audio
            one_jointed_audio_info_list.append(audio)

            print(f"当前文件时长：{tar_audio.duration_seconds}, limit：{limit}")

            if tar_audio.duration_seconds > limit:
                self.all_tasks.append(self.pool.submit(export_action, index, tar_audio, one_jointed_audio_info_list))
                index += 1
                tar_audio = None
                one_jointed_audio_info_list = []

        if tar_audio is not None:
            self.all_tasks.append(self.pool.submit(export_action, index, tar_audio, one_jointed_audio_info_list))

        return audio_info_list

    def cut_audio(self, audio_info: AudioInfo, json_info, result_list = None, split_audio = True, index = 0):
        # 参数校验
        if result_list is None:
            result_list = []
        if not os.path.exists(audio_info.path):
            print(f"fail------，切分音频失败。{audio_info.path}，文件不存在！")
            return
        if json_info is None or json_info.get("data") is None or json_info.get("data").get("utterances") is None:
            print(f"fail------，切分音频失败。{audio_info.path}，对应的json数据异常！")
            print(json_info)
            return

        num_error = 0
        info_list = json_info["data"]["utterances"]
        last_info = None
        if split_audio:
            wav_audio = AudioSegment.from_mp3(audio_info.path).set_channels(1)  # 读取未拆分的音频
        tn = gp2py.TextNormal('./edit/gp.vocab', './edit/py.vocab', add_sp1 = True, fix_er = True)
        silent = AudioSegment.silent(150)  # 前后插入300毫秒静音
        for info in info_list:
            text = info["text"]  # 中文
            if last_info is not None:
                text = last_info["text"] + text

            if not _is_all_chinese(text):
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
            if duration < 1.5 and last_info is None:
                last_info = info
                continue
            file_name = f"{audio_info.name()}_{str(index).zfill(4)}_{text}"
            if split_audio:
                seg_audio = silent + wav_audio[start_time:end_time] + silent
                seg_audio.export(os.path.join(self.cut_audio_dir, file_name + self.cut_audio_type), format(self.cut_audio_type.split(".")[-1]))
            words = info["words"]
            if last_info is not None:
                words = last_info["words"] + words
            duration_list = _words_to_duration(words)
            duration_info = " ".join(duration_list) + "|0.0|" + str('%.2f' % (float(duration) / 1000))
            (py_list, gp_list) = tn.gp2py(text)
            result_list.append(f"{file_name}|{py_list[0]}|{gp_list[0]}|{duration_info}")
            last_info = None
            index += 1
        with open(audio_info.cut_txt_path(), "w", encoding = "utf-8") as txt_f:
            txt_f.write("\n".join(result_list))
        audio_info.cut_complete = True
        audio_info.deal_complete = True