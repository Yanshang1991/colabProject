#!/usr/bin/python3
# -*- coding: utf-8 -*-
import glob
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED


def action(*args):
    print(args)


if __name__ == '__main__':
    action("asad", "asad", 1)
    # def action():
    #     max = 4
    #     for i in range(max):
    #         time.sleep(1)
    #         print(threading.current_thread().name + "  " + str(i))
    # pool = ThreadPoolExecutor(max_workers = 10)
    # tasks = [pool.submit(action) for i in range(7)]
    # wait(tasks, return_when = ALL_COMPLETED)
    # print("over")
    # # 关闭线程池
    # pool.shutdown()
    # print("close pool")
