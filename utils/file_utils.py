#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil


def exists_or_create(dir):
    """
    检查目录是否存在
    如果不存在，创建一个
    :param dir: 目录
    """
    if not os.path.exists(dir):
        os.mkdir(dir)


def cp(src, tar_dir):
    """
    复制文件
    :param src: 资源路径
    :param tar_dir: 目标路径
    """
    assert os.path.exists(src)  # 判断文件存在
    tar_dir = os.path.join(tar_dir, os.path.dirname(src))
    os.makedirs(tar_dir, exist_ok= True)

    try:
        shutil.copy(src, tar_dir)
    except IOError as e:
        print("Unable to copy file. %s" % e)






