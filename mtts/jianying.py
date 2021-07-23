import requests
import json
import os
import random
import hashlib
import zlib
from aws4 import aws4_request

'''
https://lv.ulikecam.com/activity/lv/sharevideo?template_id=6750098784123882756&from=singlemessage&isappinstalled=0
'''


def crc32(file_path):
    """
    计算文件 crc32 hash 值
    """
    with open(file_path, 'rb') as fh:
        hash = 0
        while True:
            s = fh.read(65535)
            if not s:
                break
            hash = zlib.crc32(s, hash)
        return '%08X' % (hash & 0xFFFFFFFF)


def upload_sign():
    headers = {'User-Agent': 'Cronet/TTNetVersion:c1d28325 2021-05-20 QuicVersion:47946d2a 2020-10-14', 'Content-Type': 'application/json', 'appvr': '1.4.4', 'device-time': '1626958657',
        'lan': 'zh-hans', 'loc': 'cn', 'pf': '4', 'sign': '9ea624edbaf4993b326ed127069b8c3f', 'sign-ver': '1', 'tdid': '3958721115876654',
        'x-tt-trace-id': '00-ce4af8ad0101530bc84eab0dd3890e78-ce4af8ad0101530b-01', }
    data = {'biz': 'pc-recognition'}
    data = json.dumps(data, separators = (',', ':'))
    rsp = requests.post('https://lv-pc-api.ulikecam.com/lv/v1/upload_sign', headers = headers, data = data, verify = False)
    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


def apply_upload_inner(access_key, secret_key, security_token, file_size):
    region = 'cn-north-1'
    service = 'vod'
    s = ''.join(str(random.choice('0123456789abcdefghijklmnopqrstuvwxyz')) for _ in range(10))
    params = {"Action": "ApplyUploadInner", "Version": "2020-11-19", "SpaceName": "lv-mac-recognition", "FileType": "object", "IsInner": "1", "FileSize": str(file_size), "s": s}
    rsp = aws4_request(access_key, secret_key, security_token, region, service, 'GET', 'https://vod.bytedanceapi.com', params)
    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


def commit_upload_inner(access_key, secret_key, security_token, session_key):
    region = 'cn-north-1'
    service = 'vod'
    params = {'Action': 'CommitUploadInner', 'Version': '2020-11-19', 'SpaceName': 'lv-mac-recognition', }
    data = {'SessionKey': session_key, 'Functions': []}
    data = json.dumps(data, separators = (',', ':'))
    rsp = aws4_request(access_key, secret_key, security_token, region, service, 'POST', 'https://vod.bytedanceapi.com', params, data)
    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


def audio_subtitle_submit(audio):
    headers = {'User-Agent': 'Cronet/TTNetVersion:c1d28325 2021-05-20 QuicVersion:47946d2a 2020-10-14', 'Content-Type': 'application/json', 'appvr': '1.4.4', 'device-time': '1627006156',
        'lan': 'zh-hans', 'loc': 'cn', 'pf': '4', 'sign': '544ae5c9ab1cf5a2b20b252cc34b9bac', 'sign-ver': '1', 'tdid': '473818730039',
        'x-tt-trace-id': '00-d11fc1190a6e51cc0e3756e26e880e78-d11fc1190a6e51cc-01', }
    data = {"adjust_endtime": "200", "audio": audio, "caption_type": "0", "max_lines": "1", "songs_info": [{"end_time": "40966", "id": "", "start_time": "0"}], "words_per_line": "16"}
    data = json.dumps(data, separators = (',', ':'))
    rsp = requests.post('https://lv-pc-api.ulikecam.com/lv/v1/audio_subtitle/submit', headers = headers, data = data, verify = False)
    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


def audio_subtitle_query(id):
    headers = {'User-Agent': 'Cronet/TTNetVersion:c1d28325 2021-05-20 QuicVersion:47946d2a 2020-10-14', 'Content-Type': 'application/json', 'appvr': '1.4.4', 'device-time': '1627006291',
        'lan': 'zh-hans', 'loc': 'cn', 'pf': '4', 'sign': '7c8a506fd227811a227ab127adbf416f', 'sign-ver': '1', 'tdid': '473818730039',
        'x-tt-trace-id': '00-d11fc1190a6e51cc0e3756e26e880e78-d11fc1190a6e51cc-01', }
    data = {"id": id}
    data = json.dumps(data, separators = (',', ':'))
    rsp = requests.post('https://lv-pc-api.ulikecam.com/lv/v1/audio_subtitle/query', headers = headers, data = data, verify = False)
    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


if __name__ == '__main__':




    file_path = r'./aaa.mp3'
    file_size = os.path.getsize(file_path)

    rsp = upload_sign()
    access_key = rsp['data']['access_key_id']
    secret_key = rsp['data']['secret_access_key']
    security_token = rsp['data']['session_token']

    rsp = apply_upload_inner(access_key, secret_key, security_token, file_size)
    upload_host = rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['UploadHost']
    session_key = rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['SessionKey']
    auth = rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['StoreInfos'][0]['Auth']
    store_uri = rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['StoreInfos'][0]['StoreUri']
    upload_id = rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['StoreInfos'][0]['UploadID']
    file_crc32 = str(crc32(file_path)).lower()
    with open(file_path, 'rb') as file:
        headers = {'Authorization': auth, 'Content-Type': 'application/octet-stream', 'X-Storage-U': '473818730039', 'Content-CRC32': file_crc32, 'User-Agent': 'jianying windows'

        }
        rsp = requests.request('PUT', f'https://tos.snssdk.com/{store_uri}', data = file, headers = headers, verify = False)
        print(rsp.text)

    rsp = commit_upload_inner(access_key, secret_key, security_token, session_key)
    uri = rsp['Result']['Results'][0]['Uri']

    rsp = audio_subtitle_submit(uri)
    id = rsp['data']['id']

    import time

    t1 = time.perf_counter()
    rsp = audio_subtitle_query(id)
    t2 = time.perf_counter()
    print(rsp)
    print(f'run: {t2 - t1}s')
