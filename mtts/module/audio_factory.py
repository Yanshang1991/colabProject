#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import pickle
import threading
import time
import zipfile

import yaml
from edit import audio_editor, audio_info
from audio_subtitle.audio_subtitle import AudioSubtitleParser
import util.file_utils as fu


def _write_json_response():
    with open(audio_info.json_path(), 'w') as j_f:
        json.dump(json_response, j_f)


class CutThread(threading.Thread):
    def __init__(self, cut_audio_info):
        super().__init__()
        self.cut_audio_info = cut_audio_info

    def run(self) -> None:
        editor.cut_audio(audio_info = self.cut_audio_info, json_info = json_response, result_list = result_list)
        self.cut_audio_info.cut_complete = True
        self.cut_audio_info.deal_complete = True


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type = str, help = '配置文件路径', default = r"./config.yaml")
    parser.add_argument('-w', '--workspace', type = str, help = '工作目录控件', default = r"./example_workspace")
    parser.add_argument('-i', '--raw_audio_dir', type = str, help = '原始音频目录', default = "./example_audio")
    parser.add_argument('-t', '--raw_audio_type', type = str, help = '原始音频类型')
    args = parser.parse_args()
    raw_audio_dir = args.raw_audio_dir
    assert os.path.exists(raw_audio_dir)
    raw_audio_type = args.raw_audio_type
    # 读取配置
    with open(args.config) as f:
        config = yaml.safe_load(f)
    workspace = args.workspace

    # 转换信息日志的文件名称
    audio_info_list_log_path = os.path.join(workspace, "audio_info_list.pkl")
    editor = audio_editor.AudioEditor(config = config, workspace_path = workspace)
    if os.path.exists(audio_info_list_log_path):
        print("数据文件已经存在，读取数据...")
        with open(audio_info_list_log_path, "rb") as log_f:
            audio_info_list = pickle.load(log_f)
            for audio_info in audio_info_list:
                print(f"{audio_info.path}，识别完成：{audio_info.json_record_complete}，切割完成：{audio_info.cut_complete}")
    else:
        # 合成音频
        audio_info_list = editor.joint_audio(raw_audio_dir = raw_audio_dir, raw_audio_type = raw_audio_type)
    print(f"合成音频数量：{len(audio_info_list)}")

    requester = AudioSubtitleParser(config)
    threads = []
    result_list = []
    for audio_info in audio_info_list:
        try:
            if audio_info.deal_complete:
                print(f"{audio_info.path}，已经完成处理。")
                continue

            # 调用剪映接口进行语音识别
            if audio_info.json_record_complete:  # 该数据已经完成json写入，说明是重试的数据
                print("已完成识别，从json恢复数据")
                json_response = audio_info.read_json_info()
            else:  # 把识别并把返回结果写入json
                print(f"{audio_info.path}，开始调用剪映接口识别语音")
                json_response = requester.parse(audio_info.path)
                try:
                    print(f"{audio_info.path}，开始写入json文件")
                    _write_json_response()
                    audio_info.json_record_complete = True
                    print(f"{audio_info.path}，json文件写入成功")
                except:
                    print(f"{audio_info.path}，json写入失败")

            if not audio_info.cut_complete:
                print("开始切割音频")
                cut_thread = CutThread(audio_info)
                threads.append(cut_thread)
                cut_thread.start()
        except:
            print(f"{audio_info.path}，文件转换失败！")
            continue

    while len(threads) > 0:
        time.sleep(5)
        threads = [t for t in threads if t.is_alive()]

    txt_path = os.path.join(workspace, "name_py_hz_dur.txt")
    with open(txt_path, "w", encoding = "utf-8") as txt_f:
        txt_f.write("\n".join(result_list))

    is_all_complete = True
    for audio_info in audio_info_list:
        if not audio_info.deal_complete:
            is_all_complete = False
            break

    if is_all_complete:
        zip_dst_dir = config["zip_file_path"]
        if zip_dst_dir is None:
            zip_dst_dir = workspace
        fu.zip_(zip_file_name = "data.zip", src = workspace, dst_dir = zip_dst_dir)

    with open(audio_info_list_log_path, "wb") as log_f:
        pickle.dump(audio_info_list, log_f)
