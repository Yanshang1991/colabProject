#!/usr/bin/python3
# -*- coding: utf-8 -*-
import glob
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED

import librosa
from pydub import AudioSegment


def action(*args):
    print(args)


def input_str(stra: str):
    print(stra.zfill(10))


import re

if __name__ == '__main__':
    # files = glob.glob(os.path.join("/content/aaaa/content/train/data", "*.mp3"))
    # dir = "/content/data"
    # for file in files:
    #     audio = AudioSegment.from_mp3(file.path).set_channels(1)  # 读取未拆分的音频
    #     audio.export(os.path.join(dir, os.path.split(file)[1].split(".")[0] + ".wav"), format("wav"))

    wav, r = librosa.load('102_小苗苗长成了南瓜藤.wav', 44100, "kaiser_fast")
    wav2, r2 = librosa.load('102_小苗苗长成了南瓜藤.wav')
    print(wav.shape, " ", r)
    print(wav2.shape, " ", r2)
