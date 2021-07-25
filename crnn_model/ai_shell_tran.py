# -*- coding: utf-8 -*-
import glob
import os
from pypinyin import pinyin, Style


def _get_pin_yin(s):
    pin0 = pinyin(s, Style.INITIALS)
    pin1 = pinyin(s, Style.FINALS_TONE3)
    s = ""
    print
    for i, f in zip(pin0, pin1):
        i = i[0]
        f = f[0]
        if i == "":
            i = "@"
        if len(s) == 0:
            s = i + " " + f
        else:
            s = s + " " + i + " " + f

    return s


def trans(dir, tar_dir):
    text_paths = glob.glob(os.path.join(dir, "*.trn"))
    total = len(text_paths)
    print("trn文件数量：" + str(total))

    # 显示第一个数据
    with open(text_paths[0], 'r', encoding = 'utf8') as fr:
        lines = fr.readlines()
    print("第一个数据：")
    print(lines)

    # 数据集文件trn内容读取保存到数组中
    hanzi_list = []
    pinyin_list = []
    paths = []
    for path in text_paths:
        with open(path, 'r', encoding = 'utf8') as fr:
            lines = fr.readlines()
            hanzi = lines[0].strip('\n')  # 汉字
            pinyin_ = _get_pin_yin(hanzi.replace(" ", ""))  # 汉字转成拼音
            name = os.path.basename(path).rstrip(".wav.trn")
            pinyin_list.append(name + " " + pinyin_)
            hanzi_list.append(name + " " + hanzi)
            paths.append(path.rstrip('.trn'))

    # 把汉字和拼音数据写入文件中

    print("汉字数据数据：")
    print(hanzi_list[0:10])
    print("拼音数据数据：")
    print(pinyin_list[0:10])
    print("音频文件数据数据：")
    print(paths[0:10])
    hanzi_list.sort()
    pinyin_list.sort()
    with open(os.path.join(tar_dir, "hanzi.txt"), 'wt') as F:
        F.write('\n'.join(hanzi_list))
    with open(os.path.join(tar_dir, "edit.txt"), 'wt') as F:
        F.write('\n'.join(pinyin_list))



trans("/content/data_thchs30/data/", "/content/")