#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os

def add(index):
    index += 1


if __name__ == '__main__':
    # with open("aaa.json", 'r', encoding = 'utf-8') as f:
    #     json_info = json.loads(f.read())
    #     print(json_info)
    # with open("bbb.json", "w", encoding = "utf-8") as w_f:
    #     w_f.write(json.dumps(json_info))
    # for root, dirs, files in os.walk("/content/wav/", topdown = False, followlinks = True):
    #     for file in files:
    #         (name, ext) = os.path.splitext(file)
    #         if ext == ".wav":
    #             if not os.path.exists(os.path.join(root, name + ".json")):
    #                 os.rename(os.path.join(root, file), os.path.join("/content/wav_2", file))
    index = 0
    for i in range(10):
        add(index)
        print(index)
    print(index)
