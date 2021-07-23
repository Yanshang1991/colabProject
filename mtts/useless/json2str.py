#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import json
from pypinyin import pinyin, Style


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


def get_pin_yin(s):
    pinyinlist = pinyin(s, Style.TONE3)

    def handle(ll):
        if (is_number(ll[0][-1]) or ll[0] == ' '):
            return ll[0]
        return ll[0] + '5'

    py = list(map(handle, pinyinlist))
    py = ' '.join(py)
    return py


# 检验是否全是中文字符
def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root_draft', type = str, help = '剪映草稿root文件位置，默认是window的下的路径', default = "C:\\Users\\Administrator\\AppData\\Local\\JianyingPro\\User "
                                                                                                          "Data\\Projects\\com.lveditor.draft\\root_draft_meta_info.json")
    parser.add_argument('-d', '--dst_dir', type = str, help = '生成的txt文件存放目录', default = "./workspace/txt")
    args = parser.parse_args()
    with open(args.root_draft, 'r', encoding = 'utf-8') as root_f:
        root_info = json.load(root_f)

    all_draft_info = root_info["all_draft_store"]  # 草稿列表
    dst_dir = args.dst_dir
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok = True)

    num_error = 0
    index = 0
    total_lines = []
    for draft_info in all_draft_info:
        with open(draft_info["draft_json_file"], 'r', encoding = 'utf-8') as json_f:  # json文件
            draft = json.load(json_f)
        lines = []
        for (text, segment) in zip(draft["materials"]["texts"], draft["tracks"][1]["segments"]):
            content = text["content"]
            if not is_all_chinese(content):
                num_error += 1
                print(f"内容：{content}，含有非中文字符。总数量：{num_error}")
                continue
            start = segment["target_timerange"]["start"]
            duration = segment["target_timerange"]["duration"]
            py = get_pin_yin(content)
            line = f"text{index}|{content}|{py}|{start}|{duration}"
            lines.append(line)
            total_lines.append(line)
            index += 1
        with open(os.path.join(dst_dir, draft_info["draft_name"] + '.txt'), "w", encoding = "utf-8") as txt_f:
            txt_f.write("\n".join(lines))
    with open(os.path.join(dst_dir, "all_info" + '.txt'), "w", encoding = "utf-8") as txt_f:
        txt_f.write("\n".join(total_lines))
