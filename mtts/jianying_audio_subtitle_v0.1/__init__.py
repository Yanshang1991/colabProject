#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json


if __name__ == '__main__':
    with open("aaa.json", 'r', encoding = 'utf-8') as f:
        json_info = json.loads(f.read())
        print(json_info)
    with open("bbb.json", "w", encoding = "utf-8") as w_f:
        w_f.write(json.dumps(json_info))
