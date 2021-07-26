#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import yaml
from edit import audio_editor2, audio_info
from audio_subtitle.audio_subtitle import AudioSubtitleParser
import util.file_utils as fu

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type = str, help = '配置文件路径', default = r"./config.yaml")
    parser.add_argument('-w', '--workspace', type = str, help = '工作目录控件', default = r"./example_workspace")
    parser.add_argument('-i', '--raw_audio_dir', type = str, help = '原始音频目录', default = "./example_audio")
    parser.add_argument('-t', '--raw_audio_type', type = str, help = '原始音频类型')
    parser.add_argument('-f', '--force', type = bool, help = '重新转换', default = False)
    args = parser.parse_args()
    raw_audio_dir = args.raw_audio_dir
    force = args.force
    assert os.path.exists(raw_audio_dir)
    raw_audio_type = args.raw_audio_type
    # 读取配置
    with open(args.config) as f:
        config = yaml.safe_load(f)
    workspace = args.workspace

    # 转换信息日志的文件名称
    audio_info_list_log_path = os.path.join(workspace, "audio_info_list.pkl")
    pool = ThreadPoolExecutor(4)
    all_tasks = []
    editor = audio_editor2.AudioEditor(config = config, workspace_path = workspace, pool = pool, all_tasks = all_tasks)
    requester = AudioSubtitleParser(config)
    result_list = []


    def cut_action(cur_audio_info: audio_info.AudioInfo, cur_json_response):
        editor.cut_audio(audio_info = cur_audio_info, json_info = cur_json_response, result_list = result_list)


    def recognize_action(cur_audio_info: audio_info.AudioInfo):
        print(f"{cur_audio_info.path}，开始调用剪映接口识别语音")
        json_response = requester.parse(cur_audio_info.path)
        try:
            print(f"{cur_audio_info.path}，开始写入json文件")
            with open(cur_audio_info.json_path(), 'w') as j_f:
                json.dump(json_response, j_f)
            cur_audio_info.json_record_complete = True
            print(f"{cur_audio_info.path}，json文件写入成功")
        except:
            print(f"{cur_audio_info.path}，json写入失败")
        print(f"{cur_audio_info.path}，开启线程，切分音频")
        all_tasks.append(pool.submit(cut_action, cur_audio_info, json_response))


    if os.path.exists(audio_info_list_log_path) and not force:
        print("数据文件已经存在，读取数据...")
        with open(audio_info_list_log_path, "rb") as log_f:
            audio_info_list = pickle.load(log_f)
            for audio_info in audio_info_list:
                print(f"{audio_info.path}，处理完成：{audio_info.deal_complete}，拼接完成：{audio_info.joint_complete}，识别完成：{audio_info.json_record_complete}，切割完成：{audio_info.cut_complete}")
                if audio_info.deal_complete:
                    continue
                if not audio_info.joint_complete:  # 合成未完成
                    editor.joint_audio_by_info(audio_info = audio_info, recognize_action = recognize_action)
                elif not audio_info.json_record_complete:  # 识别未完成
                    recognize_action(audio_info)
                elif not audio_info.cut_complete:  # 切割未完成
                    print("已完成识别，从json恢复数据")
                    json_response = audio_info.read_json_info()
                    all_tasks.append(pool.submit(cut_action, audio_info, json_response))

    else:
        # 合成音频
        audio_info_list = editor.joint_audio(raw_audio_dir = raw_audio_dir, raw_audio_type = raw_audio_type, recognize_action = recognize_action)

    # 等待所有线程结束
    running_tasks = [t for t in all_tasks if not t.done()]
    while len(running_tasks) > 0:
        time.sleep(5)
        print(f"还有{len(running_tasks)}个任务在执行中，等待5秒...")
        running_tasks = [t for t in all_tasks if not t.done()]
        if len(running_tasks) == 0:
            print(f"当前0个线程在执行，等待1秒，再次获取")
            time.sleep(1)
            running_tasks = [t for t in all_tasks if not t.done()]

    print("所有任务执行完成")

    # 所有线程都结束，合并标注文本
    txt_path = os.path.join(workspace, "name_py_hz_dur.txt")
    with open(txt_path, "w", encoding = "utf-8") as txt_f:
        txt_f.write("\n".join(result_list))

    # 如果所有的文件都处理完成，压缩保存整个workspace
    is_all_complete = True
    for audio_info in audio_info_list:
        if not audio_info.deal_complete:
            is_all_complete = False
            break

    if is_all_complete:
        zip_dst_dir = config["zip_file_path"]
        if zip_dst_dir is None:
            zip_dst_dir = workspace
        else:
            if not os.path.exists(zip_dst_dir):
                os.makedirs(zip_dst_dir)
        fu.zip_(zip_file_name = "data.zip", src = workspace, dst_dir = zip_dst_dir)

    with open(audio_info_list_log_path, "wb") as log_f:
        pickle.dump(audio_info_list, log_f)
