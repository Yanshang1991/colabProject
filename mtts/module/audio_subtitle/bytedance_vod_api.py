import json
import random
from aws4 import aws4_request

HOST = 'https://vod.bytedanceapi.com'
PARAMS = {'Version': '2020-11-19', 'SpaceName': 'lv-mac-recognition'}
REGION = 'cn-north-1'
SERVICE = 'vod'


def apply_upload_inner(access_key, secret_key, security_token, file_size):
    params = PARAMS.copy()
    params['Action'] = 'ApplyUploadInner'
    params['FileType'] = 'object'
    params['IsInner'] = '1'
    params['FileSize'] = str(file_size)
    params['s'] = ''.join(str(random.choice('0123456789abcdefghijklmnopqrstuvwxyz')) for _ in range(10))

    rsp = aws4_request(access_key, secret_key, security_token, REGION, SERVICE, 'GET', HOST, params)

    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)


def commit_upload_inner(access_key, secret_key, security_token, session_key):
    params = PARAMS.copy()
    params['Action'] = 'CommitUploadInner'

    data = {'SessionKey': session_key, 'Functions': []}
    data = json.dumps(data, separators = (',', ':'))

    rsp = aws4_request(access_key, secret_key, security_token, REGION, SERVICE, 'POST', HOST, params, data)

    if rsp.status_code == 200:
        return json.loads(rsp.text)
    else:
        raise RuntimeError(rsp.text)
