# -*- coding: utf-8 -*-

import os
from scipy.io import wavfile
import scipy.io.wavfile as wav
# import librosa
import numpy as np
from torch.utils.data import Dataset, DataLoader
import cv2
import argparse
import matplotlib.pyplot as plt
from scipy.fftpack import fft


class GetDataset(Dataset):

    def __init__(self, *args):
        self.file_path = args[0]  # 文件路径
        self.label_path = args[1]  # 标签文件路径
        self.params = args[2]
        self.file_name_list = []  # 文件名列表
        self.file_path_list = []  # 文件路径列表
        self.pic_path_list = []  # 频谱图路径列表
        self.file_content_list = []  # 文件内容列表
        self.file_size = 0  # 文件总数
        self.label_map = {}  # 标签map
        self._get_label_info(self.label_path)  # 生成标签数据
        self._get_file_info(self.file_path)  # 生成文件信息

    def __len__(self):
        return self.file_size

    def __getitem__(self, index):
        wav_path = self.file_path_list[index]
        transcript = self.file_content_list[index]
        image = self._wav_to_sfft(wav_path)
        if index % 10000 == 0:
            print("第%d个数据，文件名称：%s，\n标签：%s" % (index, self.file_name_list[index], transcript))
        return image, index, transcript

    def _wav_to_sfft(self, sfft_path):
        sr, y = wav.read(sfft_path)  # sr，采样率；y，数据
        stride_ms = self.params.stride_ms  # train文件中配置的参数，步幅，10ms
        window_ms = self.params.window_ms  # train文件中配置的参数
        max_freq = sr / 2
        eps = 1e-14

        stride_size = int(0.001 * sr * stride_ms)  # 160
        window_size = int(0.001 * sr * window_ms)  # 320

        truncate_size = (len(y) - window_size) % stride_size
        samples = y[:len(y) - truncate_size]  # 去掉不够一个步幅的内容，(samples - window_size) 是步幅的整数倍
        nshape = (window_size, (len(samples) - window_size) // stride_size + 1)  # (window_size, samples去除window_size 之后包含stride_size的个数+1)
        nstrides = (samples.strides[0], samples.strides[0] * stride_size)
        windows = np.lib.stride_tricks.as_strided(samples, shape = nshape, strides = nstrides)
        assert np.all(windows[:, 1] == samples[stride_size:(stride_size + window_size)])

        weighting = np.hanning(window_size)[:, None]
        # 较np.fft.fft, only  non-negative frequency saved 仅保留非负频率项，及虚部为正值
        fft = np.fft.rfft(windows * weighting, axis = 0)
        fft = np.absolute(fft)
        fft = fft ** 2

        scale = np.sum(weighting ** 2) * sr
        fft[1:-1, :] *= (2.0 / scale)
        fft[(0, -1), :] /= scale

        # Prepare fft frequency list
        freqs = float(sr) / window_size * np.arange(fft.shape[0])
        ind = np.where(freqs <= max_freq)[0][-1] + 1
        specgram = np.log(fft[:ind, :] + eps)

        specd = specgram
        specgram = (specd + 100) * 255 / 200

        # for padding , the height must be multiple by 16
        specH, specW = specgram.shape
        h_crap = (specH // 16) * 16
        resizeRatio = h_crap / specH
        resizeW = int(specW * resizeRatio)
        specgram_resize = cv2.resize(specgram, (resizeW, h_crap))

        crapW = min(specW, resizeW)

        if crapW < self.params.imgW:
            padValue = self.params.imgW - crapW
            new_specgram = np.pad(specgram_resize, ((0, 0), (0, padValue)), 'constant', constant_values = (0, 0))
        else:
            new_specgram = specgram_resize[:, :self.params.imgW]

        img = np.reshape(new_specgram, (1, h_crap, self.params.imgW)).astype(np.float32)

        return img

    def _get_file_info(self, dpath):
        file_type = ".wav"
        count_file_not_existed = 0  # 失败的个数
        file_size = 0  # 总文件数量
        for root, dirs, files in os.walk(self.file_path, topdown = False, followlinks = True):
            for name in files:
                if name.find(file_type) >= 0:
                    file_size += 1
                    path = os.path.join(root, name)
                    pure_name = name.replace(file_type, "")
                    try:
                        label_info = self.label_map[pure_name]
                        self.file_content_list.append(label_info)
                        self.file_path_list.append(path)
                        self.file_name_list.append(pure_name)
                        pic_path = os.path.join(os.getcwd(), self.params.pic_path) + '/' + pure_name + '.png'
                        self.pic_path_list.append(pic_path)
                        self.file_size += 1
                    except:
                        label_info = "file not existed"
                        count_file_not_existed += 1
                        # self.file_content_list.append(label_info)

        print("总文件数量：%d" % file_size)
        print("文件读取失败的数量：%d" % count_file_not_existed)

    def _get_label_info(self, label_path):
        assert os.path.exists(label_path)
        if os.path.isfile(label_path):
            with open(label_path, 'r', encoding = 'utf-8') as fr:
                for c in fr.readlines():
                    item = c.split(' ')
                    fileName = item[0]
                    newlabel = c.replace(fileName, "").replace("\n", "")
                    self.label_map[fileName] = newlabel
            print("标签数量：%d" % len(self.label_map))
        else:
            for root, dirs, files in os.walk(label_path, topdown = False, followlinks = True):
                for file in files:
                    if file.endswith("edit.txt"):
                        self._get_label_info(os.path.join(root, file))



