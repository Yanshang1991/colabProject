#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os

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
    list = [1, 2]
    list = [3, 4] + list
    print(list)
