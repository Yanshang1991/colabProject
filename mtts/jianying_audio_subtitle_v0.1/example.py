import argparse
import glob
import os

from audio_subtitle.audio_subtitle import AudioSubtitleParser
import json

import split


def create_parser():
    with open(r'./config.json', 'r', encoding = 'utf-8') as f:
        c = json.load(f)
    return AudioSubtitleParser(c)


def write_json_response(json_response, path):
    with open(path, 'w', encoding = "utf-8") as f:
        json.dump(json_response, f)



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src_dir', type = str, help = '要是识别的音频文件目录', default = "./")
    parser.add_argument('-t', '--audio_type', type = str, help = '音频类型，默认mp3', default = ".mp3")
    args = parser.parse_args()
    src_dir = args.src_dir
    audio_type = args.audio_type

    assert os.path.exists(src_dir)

    parser = create_parser()

    files = glob.glob(os.path.join(src_dir, "*" + audio_type))
    for file in files:
        json_response = parser.parse(file)  # 调用剪映的接口，转换数据
        (name, _) = os.path.splitext(file)
        write_json_response(json_response, name + ".json")
        print(f"{file}, 识别成功")
        name = name.split("/")[-1]
        split.split_(file, json_response, os.path.join(src_dir, name), os.path.join(src_dir, name + ".txt"), name)
        # 根据结果切分文件


