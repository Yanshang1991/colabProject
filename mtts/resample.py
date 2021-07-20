import argparse
import os

import librosa
import soundfile as sf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src', type = str, help = '要重新采样的音频文件', default = "./workspace/wav")
    parser.add_argument('-rt', '--resample_rate', type = int, help = '重新采样的频率', default = "48000")
    args = parser.parse_args()
    src = args.src
    resample_rate = args.resample_rate

    assert os.path.exists(src)

    for root, dirs, files in os.walk(src, topdown = False, followlinks = True):
        for file in files:
            (name, ext) = os.path.splitext(file)
            if not ext == ".wav":
                continue
            path = os.path.join(root, file)
            src_sig, sr = sf.read(path)  # name是要 输入的wav 返回 src_sig:音频数据  sr:原采样频率
            dst_sig = librosa.resample(src_sig, sr, resample_rate)  # resample 入参三个 音频数据 原采样频率 和目标采样频率
            sf.write(path, dst_sig, resample_rate)  # 写出数据  参数三个 ：  目标地址  更改后的音频数据  目标采样数据
