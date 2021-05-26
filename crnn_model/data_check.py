# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:10:12 2021

@author: Administrator
"""

import os
import contextlib
import wave
from scipy.io import wavfile
import librosa
import librosa.display
import numpy as np
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

fpath = r'dataset/train'
filetype = ".wav"
outputpath = r'dataset/train_pic'

for root, dirs, files in os.walk(os.path.join(os.getcwd(), fpath), topdown = False):
	for name in files:
		if name.find(filetype) >= 0:
			path = os.path.join(root, name)
			with contextlib.closing(wave.open(path, 'r')) as fr:
				frames = fr.getnframes()
				rate = fr.getframerate()
				wav_length = frames / float(rate)
				if wav_length < 1:
					print('path=%s' % path)
					os.remove(path)
