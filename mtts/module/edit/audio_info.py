#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os


class AudioInfo:
    error_seg = []
    joint_complete = False
    json_record_complete = False
    cut_complete = False
    deal_complete = False

    def __init__(self, path: str, duration_seconds: int = 0, sub_audio_info_list: list = None, id = None):
        # 文件路径
        self.path = path
        # 时长
        self.duration_seconds = duration_seconds
        # 拼接成的音频列表
        self.sub_audio_info_list = sub_audio_info_list
        # 序列号
        self.id = id

    def ext(self):
        """
        返回文件扩展名
        例如路径为：/aaaa/bbbb.mp3
        ext为：.mp3
        :return: 扩展名
        """
        if self.path is None:
            return None
        return os.path.splitext(self.path)[1]

    def name(self):
        """
        返回文件名
        例如路径为：/aaaa/bbbb.mp3
        name为：bbbb
        :return: 文件名
        """
        if self.path is None:
            return None
        return os.path.split(self.path)[-1].split(".")[0]

    def json_path(self):
        """
        返回该音频的剪映识别结果。
        如果音频路径为：/aaaa/bbbb.mp3
        则json路径为：/aaaa/bbbb.json
        :return: json存储路径
        """
        return os.path.splitext(self.path)[0] + ".json"

    def cut_txt_path(self):
        """
        返回该音频对应的：文件名、汉语、拼音、duration信息文本。
        如果音频路径为：/aaaa/bbbb.mp3
        则txt路径为：/aaaa/bbbb.txt
        :return: txt存储路径
        """
        return os.path.splitext(self.path)[0] + ".txt"

    def cut_dir_path(self):
        """
        切割文件存放目录
        :return:切割文件存放目录
        """
        return os.path.splitext(self.path)[0]

    def read_json_info(self):
        """
        读取json信息
        :return:json信息
        """
        if not self.json_record_complete:
            return None
        json_path = self.json_path()
        if not os.path.exists(json_path):
            return None
        else:
            with open(self.json_path(), 'r') as j_f:
                return json.load(j_f)
