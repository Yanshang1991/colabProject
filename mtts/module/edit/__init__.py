#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

sys.path.append('edit')


def do_action(action):
    action()


if __name__ == '__main__':
    ss:str = "adawda,"
    if ss.endswith(","):
        print(ss[0:-1])
