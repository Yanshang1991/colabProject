#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil
import time_utils as tu
import time


def cal_files(tar_dir, file_ext = None):
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
            if file_ext is None or ext == file_ext:
                count += 1

    return count


def exists_or_create(dir):
    """
    检查目录是否存在
    如果不存在，创建一个
    :param dir: 目录
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def cp(src_path, dst_path):
    """
    复制文件
    :param src: 资源路径
    :param tar_dir: 目标路径
    """
    assert os.path.exists(src_path)  # 判断文件存在
    exists_or_create(os.path.dirname(dst_path))

    try:
        shutil.copyfile(src_path, dst_path)
    except IOError as e:
        print("Unable to copy file. %s" % e)


def cpdir(src: str, dst_dir):
    """
    复制整个文件夹下的路径
    :param scr_dir: 如/content/src/ /content/src
    :param dst_path:
    :return:
    """
    print("开始复制，开始时间：%s" % tu.cur_time())
    start_time = time.time()
    sum = cal_files(tar_dir = src)

    src = src.rstrip("/")  # 移除目录末尾的/
    src_dir = os.path.dirname(src)
    index = 0
    for root, dirs, files in os.walk(src, topdown = True, followlinks = True):
        pure_path = root.replace(src_dir, "").lstrip("/")
        files_dir = os.path.join(dst_dir, pure_path)
        for file in files:
            cp(os.path.join(root, file), os.path.join(files_dir, file))
            index += 1
            # 如果总数大于200个，显示复制进度
            if sum > 200:
                print('\r' + '    [进度]:%s %.2f%%    耗时 %s' % ('>' * int(index * 50 / sum), float(index / sum * 100), tu.diff(time.time() - start_time)), end = ' ')
    print("复制完成，结束时间：%s，耗时：%s" % (tu.cur_time(), tu.diff(time.time() - start_time)))


def mv(src, tar_dir):
    shutil.move(src, tar_dir)


def walk_dir(tar_dir, file_ext, callback):
    """
    递归遍历指定的目录下的所有文件。如果文件扩展名和file_ext一样，回调callback
    :param tar_dir: 要遍历的目录，str
    :param file_ext: 要查找的扩展名，str，如".wav"
    :param callback: 回调。lambda
    """
    index = 0
    for root, dirs, files in os.walk(tar_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext is None or ext == file_ext:
                index += 1
                print('\r' + '[文件数量] %d' % index)
                callback(os.path.join(root, file), root, name, ext)


