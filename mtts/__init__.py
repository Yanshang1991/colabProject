#!/usr/bin/python3
# -*- coding: utf-8 -*-
import glob
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

if __name__ == '__main__':
    def action(max):
        for i in range(max):
            time.sleep(1)
            print(threading.current_thread().name + "  " + str(i))

    pool = ThreadPoolExecutor(4)
    future_1 = pool.submit(action, 4)
    future_2 = pool.submit(action, 4)
    future_3 = pool.submit(action, 4)
    future_4 = pool.submit(action, 4)
    future_5 = pool.submit(action, 4)
    print("over")
    # 关闭线程池
    pool.shutdown()
    print("close pool")
