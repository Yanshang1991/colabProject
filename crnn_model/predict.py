# -*- coding: utf-8 -*-
import torch
import data_convert

import os
import data_model as crnn_model
import cv2

import numpy as np
import scipy.io.wavfile as wav
from scipy.fftpack import fft
import Levenshtein
import argparse


def _img_padding(specgram, params_w):
    specH, specW = specgram.shape
    h_crap = (specH // 16) * 16
    resizeRatio = h_crap / specH
    resizeW = int(specW * resizeRatio)
    specgram_resize = cv2.resize(specgram, (resizeW, h_crap))

    crapW = min(specW, resizeW)

    if crapW < params_w:
        padValue = params_w - crapW
        new_specgram = np.pad(specgram_resize, ((0, 0), (0, padValue)), 'constant', constant_values = (0, 0))
    else:
        new_specgram = specgram_resize[:, :params_w]

    img = np.reshape(new_specgram, (1, h_crap, params_w)).astype(np.float32)

    return img, h_crap


def _gen_img2(stride_ms, window_ms, sr, samples, params_w):
    eps = 1e-14
    stride_size = int(0.001 * sr * stride_ms)
    window_size = int(0.001 * sr * window_ms)
    # extract video
    truncate_size = (len(samples) - window_size) % stride_size
    samples = samples[:len(samples) - truncate_size]
    nshape = (window_size, (len(samples) - window_size) // stride_size + 1)
    nstrides = (samples.strides[0], samples.strides[0] * stride_size)
    windows = np.lib.stride_tricks.as_strided(samples, shape = nshape, strides = nstrides)
    assert np.all(windows[:, 1] == samples[stride_size:(stride_size + window_size)])

    # Window weighting, squared Fast Fourier Transform (fft), scaling
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

    max_freq = sr / 2
    # Compute spectrogram feature
    ind = np.where(freqs <= max_freq)[0][-1] + 1
    specgram = np.log(fft[:ind, :] + eps)

    # for normalize
    specd = specgram
    specgram = (specd + 100) * 255 / 200

    # for padding
    img2, h_crap = _img_padding(specgram, params_w)

    return img2, h_crap


if __name__ == '__main__':

    # ------------------------------    定义参数    ------------------------------
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_path', type = str, default = r'/content/drive/MyDrive/t052416.pth', help = '模型路径')
    parser.add_argument('--label_file', type = str, default = r'/content/drive/MyDrive/Dataset/dataset_crnn/edit.txt', help = '拼音标签路径')
    parser.add_argument('--label_file_hanzi', type = str, default = r'/content/drive/MyDrive/Dataset/dataset_crnn/hanzi.txt', help = '汉字标签路径')
    parser.add_argument('--phoneme_file', type = str, default = r'/content/project/crnn_model/dataset/phoneme_label.txt', help = '拼音标签路径')
    parser.add_argument('--predict_video_dir', type = str, default = r'/content/drive/MyDrive/Dataset/audio/aishell3/dev/37_5622', help = '要测试的wav文件目录')
    parser.add_argument('--predict_video_size', default = 300, type = int, help = '要测试的文件数量')
    params = parser.parse_args()

    # ------------------------------    参数检查    ------------------------------
    model_path = params.model_path
    phoneme_file = params.phoneme_file
    label_file = params.label_file
    label_file_hanzi = params.label_file_hanzi
    predict_video_dir = params.predict_video_dir
    predict_video_size = params.predict_video_size
    assert os.path.exists(model_path)
    assert os.path.exists(phoneme_file)
    assert os.path.exists(predict_video_dir)

    # ------------------------------    读取数据    ------------------------------
    # 读取音素列表
    phoneme_list = []
    with open(phoneme_file, 'r') as pf:
        for c in pf.readlines():
            c = c.replace('\n', '')
            phoneme_list.append(c)

    # 读取要检测的文件名
    predict_videos = [name for name in os.listdir(predict_video_dir) if name.endswith(".wav")][0:predict_video_size]
    print("predict_videos : \nlen : " + str(len(predict_videos)) + "\n" + str(predict_videos))

    # 读取标签数据
    label_list = {label.split(" ")[0]: label.replace(label.split(" ")[0], "") for label in open(label_file).read().split('\n')}
    print("label_list : \nlen : " + str(len(label_list)))

    # 读取汉字标签数据
    label_hanzi_list = {label.split(" ")[0]: label for label in open(label_file_hanzi).read().split('\n')}
    print("label_hanzi_list : \nlen : " + str(len(label_list)))

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    converter = data_convert.strLabelConverter(phoneme_list)
    for name in predict_videos:
        video_path = os.path.join(predict_video_dir, name)  # wav文件路径
        sr, samples = wav.read(video_path)  # sr，采样率；samples，numpy array，音频数据
        params_w = 1200  # 频谱图的宽度
        img, h_crap = _gen_img2(10.0, 20.0, sr, samples, params_w)

        # ------------------------------    CRNN    ------------------------------
        nc = 1
        nclass = len(phoneme_list)
        nh = 256
        model = crnn_model.CRNN(h_crap, nc, nclass, nh)

        model.load_state_dict(torch.load(model_path, map_location = torch.device(device)))
        converter = data_convert.strLabelConverter(phoneme_list)
        testImg = torch.from_numpy(img).float().unsqueeze(0)

        # 用模型对频谱图进行预测
        preds = model(testImg)
        preds_size = torch.IntTensor([preds.size(0)])
        _, pred_result = preds.max(2)
        pred_result = pred_result.transpose(1, 0).view(-1)
        sim_preds, _ = converter.decodePhn(pred_result.data, preds_size.data, raw = False)
        str1 = ' '.join(sim_preds)
        str2 = label_list[name.split('.')[0]]
        str3 = label_hanzi_list[name.split('.')[0]]
        print("=============  compare  =============")
        print("中文标签：" + str3)
        print("拼音标签：" + str2)
        print("预测结果：" + str1)
