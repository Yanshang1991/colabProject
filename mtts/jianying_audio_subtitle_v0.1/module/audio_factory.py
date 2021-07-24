#!/usr/bin/python3
# -*- coding: utf-8 -*-
import _thread
import argparse
import json
import os
import threading

import yaml
import audio_editor
from audio_subtitle.audio_subtitle import AudioSubtitleParser


class AudioInfo:
    error_seg = []

    def __init__(self, path: str, duration_seconds: int = 0):
        # 文件路径
        self.path = path
        # 时长
        self.duration_seconds = duration_seconds

    def ext(self):
        if self.path is None:
            return None
        return os.path.splitext(self.path)[1]

    def name(self):
        if self.path is None:
            return None
        return os.path.splitext(self.path)[0]


def _write_json_response():
    with open(os.path.join(jointed_audio_dir, audio_info.name() + ".json"), 'w') as j_f:
        json.dump(json_response, j_f)


class CutThread(threading.Thread):
    def run(self) -> None:
        audio_editor.cut_audio(audio_info = audio_info, json_info = json_response, cut_wav_dir = os.path.join(workspace, "cut"), cut_audio_type = config["cut_audio_type"])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type = str, help = '配置文件路径', default = r"./config.yaml")
    parser.add_argument('-w', '--workspace', type = str, help = '工作目录控件', default = r"./workspace")
    parser.add_argument('-i', '--raw_audio_dir', type = str, help = '原始音频目录', default = "./wav")
    parser.add_argument('-t', '--raw_audio_type', type = str, help = '原始音频类型')
    args = parser.parse_args()
    raw_audio_dir = args.raw_audio_dir
    raw_audio_type = args.raw_audio_type
    # 读取配置
    with open(args.config) as f:
        config = yaml.safe_load(f)
    workspace = args.workspace

    # requester = AudioSubtitleParser(config)
    # json_response = requester.parse("/Users/ZhangBo/Documents/Python/colabProject/mtts/jianying_audio_subtitle_v0.1/module/audio_worksapce/joint/000.mp3")

    # 合成音频
    jointed_audio_dir = os.path.join(workspace, "joint")
    audio_info_list = audio_editor.joint_audio(raw_audio_dir = raw_audio_dir, jointed_audio_dir = jointed_audio_dir, raw_audio_type = raw_audio_type, jointed_audio_type = config["jointed_audio_type"],
                                               jointed_audio_limit = config["jointed_audio_limit"])
    print(f"合成音频数量：{len(audio_info_list)}")

    requester = AudioSubtitleParser(config)
    threads = []
    for audio_info in audio_info_list:
        # 调用剪映接口进行语音识别
        json_response = requester.parse(audio_info.path)

        # 保存返回的json信息
        _write_json_response()

        cut_thread = CutThread()
        cut_thread.start()
        cut_thread.join()


        # def cut():
        #     audio_editor.cut_audio(audio_info = audio_info, json_info = json_response, out_wav_dir = os.path.join(workspace, "cut"), out_audio_type = config["out_audio_type"])
        #
        #
        # print(f"开启线程切割音频{audio_info.name()}")
        # # 开启线程切割音频
        # try:
        #     _thread.start_new_thread(cut, (f"线程：{audio_info.name()}", 2,))
        # except:
        #     print("Error: 无法启动线程")
