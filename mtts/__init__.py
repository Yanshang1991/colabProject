#!/usr/bin/python3
# -*- coding: utf-8 -*-
import glob
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
from typing import List, Union

import librosa
from pydub import AudioSegment


def action(*args):
    print(args)


def input_str(stra: Union[str, List]):
    print(stra.append())


if __name__ == '__main__':
    segments: List[str] = ["123456", "1234", "12"]
    n = 6
    segments = [' '.join((s.split() * n)[:n]) if len(s.split()) != n else s for s in segments]
    print("123456".split())
