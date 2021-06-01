#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil
import time_utils as tu
import time
import zipfile


def print_process(name, cur_size, max_size, time_cost):
    print('\r[%s]: %s %.2f%%    耗时: %s' % (name, '>' * int(cur_size * 50 / max_size), float(cur_size / max_size * 100), time_cost), end = ' ')


def cal_files(tar_dir, file_exts = None):
    """
    统计目录下指定类型文件的数量。递归
    :param tar_dir: 目录
    :param file_exts: 文件名后缀，如".wav"
    :return: 数量
    """
    count = 0
    for root, dirs, files in os.walk(tar_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if file_exts is None or ext in file_exts:
                count += 1
                print('\r' + '[文件数量] %d' % count, end = ' ')

    return count


def exists_or_create(dir):
    """
    检查目录是否存在
    如果不存在，创建一个
    :param dir: 目录
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def cp(src, dst_dir):
    """
    复制文件
    :param src: 资源路径
    :param tar_dir: 目标路径
    """
    assert os.path.exists(src)  # 判断文件存在
    if os.path.isfile(src):
        exists_or_create(os.path.dirname(dst_dir))
        try:
            shutil.copyfile(src, dst_dir)
        except IOError as e:
            print("Unable to copy file. %s" % e)
    else:
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
                    print_process("复制进度", index, sum, tu.diff(time.time() - start_time))
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
    for root, dirs, files in os.walk(tar_dir, topdown = False, followlinks = True):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext is None or ext == file_ext:
                callback(os.path.join(root, file), root, name, ext)


def zip_(zip_file_name, src, dst_dir = None, file_types = None):
    """
    把目录或者文件进行压缩
    :param zip_file_name: 压缩文件名，例如aaa.zip
    :param src: 要压缩的文件或者目录
    :param dst_dir: 压缩文件存放目录。默认存放在压缩目录下。
    :param file_types: 要压缩的文件类型列表。默认为空，全部压缩
    """
    print("开始压缩，\nsrc = %s \n%s" % (src, tu.cur_time()))
    start_time = time.time()
    if dst_dir is None:
        dst_path = zip_file_name
    else:
        dst_path = os.path.join(dst_dir, zip_file_name)
        exists_or_create(dst_dir)

    if os.path.isfile(src):
        with zipfile.ZipFile(dst_path, 'w') as z:
            z.write(src)
    else:
        count = cal_files(src, file_types)
        index = 0
        with zipfile.ZipFile(dst_path, 'w') as z:
            for root, dirs, files in os.walk(src):
                for file in files:
                    name, ext = os.path.splitext(file)
                    if file != zip_file_name and (file_types is None or ext in file_types):
                        filepath = os.path.join(root, file)
                        z.write(filepath)
                        index += 1
                        print_process("压缩进度", index, count, tu.diff(time.time() - start_time))
    print("完成压缩，\n%s，%s，总耗时：%s" % (src, tu.cur_time(), tu.diff(time.time() - start_time)))


def zip_add(zip_file_path, src):
    """
    把文件或者目录添加到已有的zip文件中
    :param zip_file_path: zip文件路径
    :param src:
    :return:
    """
    assert os.path.exists(zip_file_path)
    assert os.path.exists(src)
    if os.path.isfile(src):
        with zipfile.ZipFile(zip_file_path, 'a') as z:
            z.write(src)
    else:
        with zipfile.ZipFile(zip_file_path, 'a') as z:
            for root, dirs, files in os.walk(src):
                for single_file in files:
                    if single_file != zip_file_path:
                        filepath = os.path.join(root, single_file)
                        z.write(filepath)


def unzip(zip_file_path, dst = None):
    assert os.path.exists(zip_file_path)
    exists_or_create(dst)
    with zipfile.ZipFile(zip_file_path, 'r') as z:
        z.extractall(path = dst)


unzip("aaa.zip")
