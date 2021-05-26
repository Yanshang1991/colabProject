# -*- coding: utf-8 -*-
"""
Created on Wed May 12 14:58:02 2021

@author: Administrator
"""

import torch
import data_convert

import os
import data_model as crnn_model
import cv2

import numpy as np
import scipy.io.wavfile as wav
from scipy.fftpack import fft
import Levenshtein


def _genImg1(*args):
    stride_ms = args[0]
    window_ms = args[1]
    sr= args[2] 
    samples = args[3]
    params_w = args[4]
    eps = 1e-14
    
    stride_size = int(0.001 * sr * stride_ms)
    window_size = int(0.001 * sr * window_ms)
    # extract video
    truncate_size = (len(samples) - window_size) % stride_size
    samples = samples[:len(samples) - truncate_size]
    nshape = (window_size, (len(samples) - window_size) // stride_size + 1)
    nstrides = (samples.strides[0], samples.strides[0] * stride_size)
    windows = np.lib.stride_tricks.as_strided(samples,shape = nshape, strides = nstrides)
    assert np.all(windows[:, 1] == samples[stride_size:(stride_size + window_size)])
 
    x = np.linspace(0, window_size - 1, window_size, dtype=np.int32)
    w = 0.54 - 0.46 * np.cos(2 * np.pi * (x) / (window_size - 1))  # 汉明窗

    # window_length = fs / 1000 * window_ms # 计算窗长度的公式，目前全部为400固定值
    wav_arr = np.array(samples)
    # wav_length = len(samples)
    range0_end = int(len(samples) / sr * 1000 - window_ms) // int(stride_ms)  # 计算循环终止的位置，也就是最终生成的窗数
    data_input = np.zeros((range0_end, window_size // 2), dtype=np.float)  # 用于存放最终的频率特征数据
    data_line = np.zeros((1, window_size // 2), dtype=np.float)
    for i in range(0, range0_end):
        p_start = i * stride_size
        p_end = p_start + window_size
        data_line = wav_arr[p_start:p_end]
        data_line = data_line * w  # 加窗
        data_line = np.abs(fft(data_line))   # 此fft 为函数变化
        data_input[i] = data_line[0:window_size // 2]  # 取一半数据，因为是对称的
    data_input1 = np.log(data_input + 1)
    specgram = data_input1.T
    
    # for normalize 
    specd = specgram
    specMax = np.max(specgram)
    specMin = np.min(specgram)
    dif = specMax - specMin
    specgram = (specd - specMin) * 255 / dif
    
    # for padding    
    img1,h_crap =_imgPadding(specgram,params_w)
    
    return img1,h_crap
    
    
def _imgPadding(specgram,params_w):    
    
    specH, specW = specgram.shape
    h_crap = (specH // 16) * 16
    resizeRatio = h_crap / specH
    resizeW = int(specW * resizeRatio)
    specgram_resize = cv2.resize(specgram, (resizeW, h_crap))

    crapW = min(specW, resizeW)

    if crapW < params_w:
        padValue = params_w - crapW
        new_specgram = np.pad(specgram_resize, ((0, 0), (0, padValue)), 'constant', constant_values=(0, 0))
    else:
        new_specgram = specgram_resize[:, :params_w]
    
    img = np.reshape(new_specgram, (1, h_crap, params_w)).astype(np.float32)
    
    return img, h_crap
    
    
def _genImg2(*args): 
    stride_ms = args[0]
    window_ms = args[1]
    sr= args[2] 
    samples = args[3]
    params_w = args[4]
    eps = 1e-14
    
    
    stride_size = int(0.001 * sr * stride_ms)
    window_size = int(0.001 * sr * window_ms)
    # extract video
    truncate_size = (len(samples) - window_size) % stride_size
    samples = samples[:len(samples) - truncate_size]
    nshape = (window_size, (len(samples) - window_size) // stride_size + 1)
    nstrides = (samples.strides[0], samples.strides[0] * stride_size)
    windows = np.lib.stride_tricks.as_strided(samples,shape = nshape, strides = nstrides)
    assert np.all(windows[:, 1] == samples[stride_size:(stride_size + window_size)])
     
    # Window weighting, squared Fast Fourier Transform (fft), scaling
    weighting = np.hanning(window_size)[:, None]

    # 较np.fft.fft, only  non-negative frequency saved 仅保留非负频率项，及虚部为正值
    fft = np.fft.rfft(windows * weighting, axis=0)
    fft = np.absolute(fft)
    fft = fft**2
    
    scale = np.sum(weighting**2) * sr
    fft[1:-1, :] *= (2.0 / scale)
    fft[(0, -1), :] /= scale
    
    # Prepare fft frequency list
    freqs = float(sr) / window_size * np.arange(fft.shape[0])

    max_freq=sr/2
    # Compute spectrogram feature
    ind = np.where(freqs <= max_freq)[0][-1] + 1
    specgram = np.log(fft[:ind, :] + eps)  
    
     # for normalize 
    specd = specgram
    specgram = (specd + 100) * 255 / 200
    
    # for padding    
    img2,h_crap =_imgPadding(specgram,params_w)
    
    return img2,h_crap
    
    
    
if __name__ == '__main__':
    model_path = r'./t0510.pth'    
    phoneme_file=r'dataset/transcript/phoneme_label5.txt'
    
    train_video=r'./dataset/train/S0002/BAC009S0002W0122.wav'
    test_video=r'./BAC009S0916W0495.wav'
    microphone=r'./mirocphone_test1.wav'
    
    if phoneme_file != '':
        phoneme_list = []
        phoneme_file = os.path.join(os.getcwd(), phoneme_file)
        with open(phoneme_file, 'r', encoding='utf-8') as fr:
            for c in fr.readlines():
               c = c.replace("\n", "")
               phoneme_list.append(c)
    
    # ------------------------input the wav file 
    sr,samples= wav.read(train_video)
    params_w=1200
    
    # img,h_crap = _genImg1(10.0, 20.0,sr,samples,params_w)
    img,h_crap = _genImg2(10.0, 20.0,sr,samples,params_w)
 
    # model train 
    model1=r'./t0510.pth'
    model2='./t0512.pth'
    
    # model_path=model1
    model_path=model2
    # cnn and rnn
    nc=1
    nclass=len(phoneme_list)
    nh=256

    model = crnn_model.CRNN(h_crap, nc, nclass, nh)

#    model.load_state_dict(torch.load(model_path))
    model.load_state_dict(torch.load(model_path,map_location=torch.device('cpu')))


    converter = data_convert.strLabelConverter(phoneme_list)
    testImg=torch.from_numpy(img).float().unsqueeze(0)


    Text='@ er2 d uei4 l ou2 sh i4 ch eng2 j iao1 @ i4 zh i4 z uo4 @ iong4 z uei4 d a4 d e x ian4 g ou4'
# test_Text='zh e4 l ing4 b ei4 d ai4 k uan3 d e @ van2 g ong1 m en q in3 sh i2 n an2 @ an1'
    testText=[]
    testText.append(Text)
    t, l = converter.encodePhn(testText)
    
    # model predict
    preds=model(testImg)
    preds_size = torch.IntTensor([preds.size(0)])

    _, pred_result = preds.max(2)
    # pred_result = pred_result.squeeze(2)
    # pred_result = pred_result.transpose(1, 0).contiguous().view(-1)
    pred_result = pred_result.transpose(1, 0).view(-1)
    sim_preds,_ = converter.decodePhn(pred_result.data, preds_size.data, raw=False)
    
    # compare string 
    str1=' '.join(sim_preds)
    str2=Text
    corr=Levenshtein.ratio(str1, str2)
    print("=============  compare  =============")
    print(str2)
    print('\n')
    print(str1)
    print( 'the similarity between sample and predict is %3.2f' %(corr))








