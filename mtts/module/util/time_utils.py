#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from datetime import datetime, timezone, timedelta


def cur_time():
    """
    返回当前时间
    :return: 当前时间，如：2021-05-27 02:29:12.096762+08:00
    """
    dt = datetime.utcnow().replace(tzinfo = timezone.utc)
    diff_8 = timezone(timedelta(hours = 8))
    return dt.astimezone(diff_8)



def diff(seconds):
    """
    把秒转成时间
    :param seconds:
    :return:
    """
    s = ""
    hours = seconds / 3600
    if hours > 0:
        s = "%d小时 " % hours

    seconds = seconds % 3600
    minutes = seconds / 60
    s = s + ("%d分 " % minutes)

    seconds = seconds % 60

    s = s + ("%d秒 " % seconds)
    return s


