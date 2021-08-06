from bytedance_vod_api import HOST
import requests
import json
import time

HOST = 'https://lv-pc-api.ulikecam.com'
HEADERS = {'User-Agent': 'Cronet/TTNetVersion:c1d28325 2021-05-20 QuicVersion:47946d2a 2020-10-14', 'appvr': '1.4.4', 'lan': 'zh-hans', 'loc': 'cn', 'pf': '4', 'sign-ver': '1',
           'x-tt-trace-id': '00-ce4af8ad0101530bc84eab0dd3890e78-ce4af8ad0101530b-01', }
appvr = '1.4.4'


def upload_sign(device_time, tdid, sign):
    headers = HEADERS.copy()
    headers['device-time'] = device_time
    headers['tdid'] = tdid
    headers['sign'] = sign

    data = {'biz': 'pc-recognition'}
    data = json.dumps(data, separators = (',', ':'))

    rsp = requests.post(HOST + '/lv/v1/upload_sign', headers = headers, data = data)
    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


def audio_subtitle_submit(audio, device_time, tdid, sign):
    headers = HEADERS.copy()
    headers['device-time'] = device_time
    headers['tdid'] = tdid
    headers['sign'] = sign

    data = {'adjust_endtime': '200', 'audio': audio, 'caption_type': '0', 'max_lines': '1', 'songs_info': [{'end_time': '40966', 'id': '', 'start_time': '0'}], 'words_per_line': '16'}
    data = json.dumps(data, separators = (',', ':'))

    rsp = requests.post(HOST + '/lv/v1/audio_subtitle/submit', headers = headers, data = data)

    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


def audio_subtitle_query(id, device_time, tdid, sign):
    headers = HEADERS.copy()
    headers['device-time'] = device_time
    headers['tdid'] = tdid
    headers['sign'] = sign

    data = {'id': id}
    data = json.dumps(data, separators = (',', ':'))

    rsp = requests.post(HOST + '/lv/v1/audio_subtitle/query', headers = headers, data = data)

    if rsp.status_code == 200:
        json_response = json.loads(rsp.text)
        if not json_response["errmsg"] == "success":
            print("剪映，query接口获取内容为空，重新发起请求")
            time.sleep(1)
            audio_subtitle_query(id, device_time, tdid, sign)
        else:
            # print(f"剪映，query接口响应\n{rsp.text}")
            return json_response
    elif rsp.status_code == 504:
        print("剪映，query接口504，重新发起请求")
        time.sleep(1)
        audio_subtitle_query(id, device_time, tdid, sign)
    else:
        raise RuntimeError(rsp.text)
