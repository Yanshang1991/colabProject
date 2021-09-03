#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import glob
import random
import time
from concurrent.futures import ThreadPoolExecutor

from pydub import AudioSegment

import gp2py
import numpy as np
from audio_info import AudioInfo
import threading


def _is_all_chinese(_input_text):
    # 检验是否全是中文字符
    for _char in _input_text:
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
        self.index = 0
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

    def gen_audio_info(self, raw_audio_dir: str, recognize_action, raw_audio_type: str = None, cut_audio_dir = None, cut_audio_type = None):
        # 参数校验
        assert os.path.exists(raw_audio_dir)
        # 获取音频文件
        file_match_path = os.path.join(raw_audio_dir, "*")
        if raw_audio_type is not None:
            file_match_path += raw_audio_type
        files = glob.glob(file_match_path)
        audio_info_list = [AudioInfo(path = f, cut_audio_dir = cut_audio_dir, cut_audio_type = cut_audio_type) for f in files]
        for audio_info in audio_info_list:
            audio_info.joint_complete = True
            self.all_tasks.append(self.pool.submit(recognize_action, audio_info))  # recognize_action(audio_info)
        return audio_info_list

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
            tar_audio_path = os.path.join(self.jointed_audio_dir, str(cur_index).zfill(3) + self.jointed_audio_type)
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

    def _get_duration(self, jointed_info_list):
        end_time = jointed_info_list[-1]['end_time']
        start_time = jointed_info_list[0]['start_time']
        duration = end_time - start_time
        return duration, start_time, end_time

    def _get_name(self, jointed_info_list):
        all_text: str = None
        for info in jointed_info_list:
            text = info["text"]
            if all_text is None:
                all_text = text
            else:
                all_text += ","
                all_text += text
        if all_text.endswith(","):
            all_text = all_text[0:-1]
        return all_text

    def _get_duration_segment(self, jointed_info_list):
        words = None
        for info in jointed_info_list:
            if words is None:
                words = info["words"]
            else:
                gap_start_time = words[-1]["end_time"]
                gap_end_time = info["start_time"]
                words.append({"start_time": gap_start_time, "end_time": gap_end_time})
                words = words + info["words"]
        return _words_to_duration(words)

    def cut_audio(self, audio_info: AudioInfo, json_info, result_list = None, split_audio = True, index = 0):
        # 参数校验
        try:
            self.index += 1
            if result_list is None:
                result_list = []
            if not os.path.exists(audio_info.path):
                print(f"fail------，切分音频失败。{audio_info.path}，文件不存在！")
                return

            num_error = 0
            info_list = json_info["data"]["utterances"]
            if split_audio:
                wav_audio = AudioSegment.from_file(audio_info.path)  # 读取未拆分的音频
            print(f"音频读取成功")
            tn = gp2py.TextNormal('./edit/gp.vocab', './edit/py.vocab', add_sp1 = True, fix_er = True)
            silent = AudioSegment.silent(150)  # 前后插入300毫秒静音
            jointed_info_list = None
            cur_result_list = []
            for info in info_list:
                if not _is_all_chinese(info["text"]):
                    num_error += 1
                    content = info["text"]
                    # print(f"内容：{content}，含有非中文字符。总数量：{num_error}")
                    continue

                if jointed_info_list is None:
                    jointed_info_list = [info]
                    continue
                else:
                    duration, start_time, end_time = self._get_duration(jointed_info_list)
                    split_limit: int = self.config["split_limit"]
                    if not split_limit == 0:
                        split_limit = random.randint(split_limit, split_limit + 2)

                    if duration / 1000 > split_limit:  # 时间大于10秒，不再拼接
                        text = self._get_name(jointed_info_list)
                        file_name = f"{str(1000 * self.index + index).zfill(4)}_{text}"
                        if split_audio:
                            seg_audio = silent + wav_audio[start_time:end_time] + silent
                            seg_audio.export(os.path.join(self.cut_audio_dir, file_name + self.cut_audio_type), format(self.cut_audio_type.split(".")[-1]))

                        duration_list = self._get_duration_segment(jointed_info_list)
                        duration_info = " ".join(duration_list) + "|0.0|" + str('%.2f' % (float(duration) / 1000))
                        (py_list, gp_list) = tn.gp2py(text)
                        text_info = f"{file_name}|{py_list[0]}|{gp_list[0]}|{duration_info}"
                        result_list.append(text_info)
                        cur_result_list.append(text_info)
                        jointed_info_list = None
                        index += 1
                    else:
                        jointed_info_list.append(info)

            with open(audio_info.cut_txt_path(), "w", encoding = "utf-8") as txt_f:
                txt_f.write("\n".join(cur_result_list))
            audio_info.cut_complete = True
            audio_info.deal_complete = True
            print(f"{audio_info.path}，切分完成")
        except Exception as e:
            print(e)
