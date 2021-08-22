#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ctypes

if __name__ == '__main__':
    so = ctypes.cdll.LoadLibrary("./libencrypt.so")

    print(so)
