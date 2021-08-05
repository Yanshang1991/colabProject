#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re

han_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
unit_list = ["", "", "十", "百", "千", "万", "十", "百", "千", "亿"]


def _2_gp(_input_text: str):
    """
    把数字转成汉字
    :param _input_text: 文本
    :return: 输出文本
    """
    dot_list = re.findall(r'\.\d+', _input_text)
    for dot in dot_list:
        _input_text = _input_text.replace(dot, _to_han_pure(dot))

    year_list = re.findall(r'\d+年', _input_text)
    for year in year_list:
        _input_text = _input_text.replace(year, _to_han_pure(year))

    percent_list = re.findall(r'\d+%', _input_text)
    for percent in percent_list:
        _input_text = _input_text.replace(percent, _to_han_percent(percent))

    n_list = re.findall(r'\d+', _input_text)

    # 按照长度倒叙，避免短的先把长的替换掉
    def sort_by_len(elem):
        return len(elem)

    n_list.sort(key = sort_by_len, reverse = True)
    for n_str in n_list:
        if len(n_str) > 9:
            _input_text = _input_text.replace(n_str, _to_han_pure(n_str))
        else:
            _input_text = _input_text.replace(n_str, _to_han(n_str))
    return _input_text


def _to_han_pure(num_str):
    for _char in num_str:
        if _char.isdigit():
            num = int(_char)
            num_str = num_str.replace(_char, han_list[num])
    return num_str


def _to_han_percent(num_str: str):
    num_str = num_str[0:-1]
    return "百分之" + _to_han(num_str)


def _to_han(num_str):
    result = ""
    num_len = len(num_str)
    for i in range(num_len):
        num = int(num_str[i])
        if i != num_len - 1:
            if num != 0:
                result = result + han_list[num] + unit_list[num_len - i]
            else:
                if result[-1] == '零':
                    continue
                else:
                    result = result + '零'
        else:
            if num != 0:
                result += han_list[num]
    while result.endswith(han_list[0]):
        result = result[0:-1]
    if num_len == 2:
        result = result.replace("一十", "十")
    elif num_len == 6:
        result = result[0:2].replace("一十", "十")
    return result


if __name__ == '__main__':
    print(_2_gp("今年是2021年，17月1日，100%，100，101，1010, 1121.21"))
