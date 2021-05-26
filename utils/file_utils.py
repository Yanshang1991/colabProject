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
    tar_dir = os.path.join(tar_dir, os.path.basename(src))
    os.makedirs(tar_dir, exist_ok = True)

    try:
        shutil.copyfile(src, tar_dir)
    except IOError as e:
        print("Unable to copy file. %s" % e)


def mv(src, tar_dir):
    shutil.move(src, tar_dir)


def walk_dir(tar_dir, file_ext, callback):
    """
    递归遍历指定的目录下的所有文件。如果文件扩展名和file_ext一样，回调callback
    :param tar_dir: 要遍历的目录，str
    :param file_ext: 要查找的扩展名，str，如".wav"
    :param callback: 回调。lambda
    """
    for root, dirs, files in os.walk(tar_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == file_ext:
                callback(os.path.join(root, file), root, name, ext)


def cal_files(tar_dir, file_ext):
    """
    统计目录下指定类型文件的数量。递归
    :param tar_dir: 目录
    :param file_ext: 文件名后缀，如".wav"
    :return: 数量
    """
    count = 0
    for root, dirs, files in os.walk(tar_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == file_ext:
                count += 1

    return count
