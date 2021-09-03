#!/usr/bin/python3
# -*- coding: utf-8 -*-
from scipy.io import wavfile
import numpy as np

class soundBase:
    def __init__(self, path):
        self.path = path

    def audioread(self, formater='sample'):
        """
        读取语音文件
        2020-2-26   Jie Y.  Init
        这里的wavfile.read()函数修改了里面的代码，返回项return fs, data 改为了return fs, data, bit_depth
        如果这里报错，可以将wavfile.read()修改。
        :param formater: 获取数据的格式，为sample时，数据为float32的，[-1,1]，同matlab同名函数. 否则为文件本身的数据格式
                        指定formater为任意非sample字符串，则返回原始数据。
        :return: 语音数据data, 采样率fs，数据位数bits
        """
        fs, data = wavfile.read(self.path)
        # if formater == 'sample':
        #     data = data / (2 ** (bits - 1))
        return data, fs

    def SPL(self, data, fs, frameLen=100, isplot=True):
        """
        计算声压曲线
        2020-2-26   Jie Y.  Init
        :param data: 语音信号数据
        :param fs: 采样率
        :param frameLen: 计算声压的时间长度(ms单位)
        :param isplot: 是否绘图，默认是
        :return: 返回声压列表spls
        """

        def spl_cal(s, fs, frameLen):
            """
            根据数学公式计算单个声压值
            $y=\sqrt(\sum_{i=1}^Nx^2(i))$
            2020-2-26   Jie Y. Init
            :param s: 输入数据
            :param fs: 采样率
            :param frameLen: 计算声压的时间长度(ms单位)
            :return: 单个声压数值
            """
            l = len(s)
            M = frameLen * fs / 1000
            if not l == M:
                exit('输入信号长度与所定义帧长不等！')
            # 计算有效声压
            pp = 0
            for i in range(int(M)):
                pp += (s[i] * s[i])
            pa = np.sqrt(pp / M)
            p0 = 2e-5
            spl = 20 * np.log10(pa / p0)
            return spl

        length = len(data)
        M = fs * frameLen // 1000
        m = length % M
        if not m < M // 2:
            # 最后一帧长度不小于M的一半
            data = np.hstack((data, np.zeros(M - m)))
        else:
            # 最后一帧长度小于M的一半
            data = data[:M * (length // M)]
        spls = np.zeros(len(data) // M)
        for i in range(length // M - 1):
            s = data[i * M:(i + 1) * M]
            spls[i] = spl_cal(s, fs, frameLen)

        if isplot:
            plt.subplot(211)
            plt.plot(data)
            plt.subplot(212)
            plt.step([i for i in range(len(spls))], spls)
            plt.show()
        return spls


sb = soundBase('b.wav')
data, fs = sb.audioread()
sb.SPL(data, fs)