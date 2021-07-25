import requests
import os
import zlib
import bytedance_vod_api
import lv_ulikecam_api

def _crc32(file_path):
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


class AudioSubtitleParser:

    def __init__(self, config):
       self.config = config

    def parse(self, file_path):
        file_size = os.path.getsize(file_path)

        upload_sign_config = self.config['upload_sign']
        rsp = lv_ulikecam_api.upload_sign(upload_sign_config['device_time'], upload_sign_config['tdid'], upload_sign_config['sign'])
        access_key = rsp['data']['access_key_id']
        secret_key = rsp['data']['secret_access_key']
        security_token = rsp['data']['session_token']

        rsp = bytedance_vod_api.apply_upload_inner(access_key, secret_key, security_token, file_size)
        upload_host=rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['UploadHost']
        session_key=rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['SessionKey']
        auth = rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['StoreInfos'][0]['Auth']
        store_uri = rsp['Result']['InnerUploadAddress']['UploadNodes'][0]['StoreInfos'][0]['StoreUri']

        file_crc32 = str(_crc32(file_path)).lower()
        with open(file_path, 'rb') as file:
            headers = {
                'Authorization':auth,
                'Content-Type': 'application/octet-stream',
                'X-Storage-U': '473818730039',
                'Content-CRC32': file_crc32,
                'User-Agent': 'jianying windows'

            }
            requests.request('PUT', f'https://{upload_host}/{store_uri}', data=file, headers=headers)
        
        rsp = bytedance_vod_api.commit_upload_inner(access_key, secret_key, security_token, session_key)
        uri = rsp['Result']['Results'][0]['Uri']
        
        audio_subtitle_submit_config = self.config['audio_subtitle_submit']
        rsp = lv_ulikecam_api.audio_subtitle_submit(uri, audio_subtitle_submit_config['device_time'], audio_subtitle_submit_config['tdid'], audio_subtitle_submit_config['sign'])
        id = rsp['data']['id']

        audio_subtitle_query_config = self.config['audio_subtitle_query']
        rsp = lv_ulikecam_api.audio_subtitle_query(id, audio_subtitle_query_config['device_time'], audio_subtitle_query_config['tdid'], audio_subtitle_query_config['sign'])

        return rsp