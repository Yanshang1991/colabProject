#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

sys.path.append('edit')


def do_action(action):
    action()


if __name__ == '__main__':
    def my_action():
        print("do_action")


    do_action(my_action)
