import datetime
import requests
import hashlib
import hmac
from urllib import parse


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signature_key(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning


def aws4_request(access_key, secret_key, security_token, region, service, method, url, params = None, data = None, headers = None):
    method = method.upper()

    scheme, netloc, path, query, fragment = parse.urlsplit(url)
    query_params = parse.parse_qs(query)
    if params:
        for k, v in params.items():
            if k not in query_params:
                query_params[k] = [v]
            else:
                query_params[k].append(v)
    query = parse.urlencode(sorted(query_params.items(), key = lambda d: d[0]), doseq = True)

    t = datetime.datetime.utcnow()
    # t = datetime.datetime.strptime('20210722T171304Z', '%Y%m%dT%H%M%SZ')
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

    canonical_uri = '/' if path == '' else path
    canonical_querystring = query
    if data:
        payload_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        canonical_headers = 'x-amz-content-sha256:' + payload_hash + '\n' + 'x-amz-date:' + amzdate + '\n' + 'x-amz-security-token:' + security_token + '\n'
        signed_headers = 'x-amz-content-sha256;x-amz-date;x-amz-security-token'
    else:
        payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()
        canonical_headers = 'x-amz-date:' + amzdate + '\n' + 'x-amz-security-token:' + security_token + '\n'
        signed_headers = 'x-amz-date;x-amz-security-token'

    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    signing_key = get_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    headers = headers if headers else {}
    headers['x-amz-date'] = amzdate
    headers['x-amz-security-token'] = security_token
    if data:
        headers['x-amz-content-sha256'] = payload_hash
    headers['Authorization'] = authorization_header

    return requests.request(method, parse.urlunsplit((scheme, netloc, path, query, fragment)), data = data, headers = headers, verify = False)


if __name__ == '__main__':
    import json

    access_key = 'AKTPZGI4MWJjMjdiN2IzNGJlYjk3OWZhMmRjYTcwOWRlODE'
    secret_key = 'f/EiqXK16MAiMRk1bqfNsup1HGTxYpsxu2CBUA0xZueQd+xw6tzJ5xIJ/gtp1bLw'
    security_token = 'STS2eyJMVEFjY2Vzc0tleUlkIjoiQUtMVE9XTmxOVE0wWWpJeVpHUXlORGd3TW1JeE9EUXdPV1F6TUdZNVpUYzVNamsiLCJBY2Nlc3NLZXlJZCI6IkFLVFBaR0k0TVdKak1qZGlOMkl6TkdKbFlqazNPV1poTW1SallUY3dPV1JsT0RFIiwiU2lnbmVkU2VjcmV0QWNjZXNzS2V5IjoiMkZTM3BlVG13Q2dYM2tSZmplYnBlTzZSeGVScDI0cUtnQWR4Yy9TOEhmd0hwQ2JScVAxU3VWNVY3WnU4aWluRHgzMGZHcCtJUWtQMzZaOFhXKzdRT1VEWFFiVEREWjJsR21LNkg1NlNZUlE9IiwiRXhwaXJlZFRpbWUiOjE2MjY5Nzc1ODEsIlBvbGljeVN0cmluZyI6IntcIlN0YXRlbWVudFwiOlt7XCJFZmZlY3RcIjpcIkFsbG93XCIsXCJBY3Rpb25cIjpbXCJ2b2Q6KlwiXSxcIlJlc291cmNlXCI6W1wiKlwiXX1dfSIsIlNpZ25hdHVyZSI6ImMwNjU3YTFlZTQ0OTkwOWIzZGU0YzY2NzgyZmUyYTdhMTc5ZmYxOGJiMzZiNjQzNDg0MWQyOTNlYzdkNzUzNDYifQ=='
    region = 'cn-north-1'
    service = 'vod'

    # params = {
    #     'Action':'ApplyUploadInner',
    #     'Version':'2020-11-19',
    #     'SpaceName':'lv-mac-recognition',
    #     'FileType':'object',
    #     'IsInner':'1',
    #     'FileSize':'656475',
    #     's':'5yrk8m4pq7s'
    # }
    # rsp = aws4_request(access_key , secret_key, security_token, region, service, 'GET', 'http://vod.bytedanceapi.com', params)
    # print(rsp.text)

    params = {'Action': 'CommitUploadInner', 'Version': '2020-11-19', 'SpaceName': 'lv-mac-recognition', }
    data = {'SessionKey': 'eyJhcHBJZCI6IiIsImJpelR5cGUiOiIiLCJmaWxlVHlwZSI6Im9iamVjdCIsImxlZ2FsIjoiIiwidXJpIjoidG9zLWNuLXYtMjI1NzRmL2ZiMTZjNWEzM2RhNTQ0NzM5NjhjMWYyZmU0YjIzOGJiIiwidXNlcklkIjoiIn0=',
            'Functions': []}
    data = json.dumps(data, separators = (',', ':'))
    rsp = aws4_request(access_key, secret_key, security_token, region, service, 'POST', 'https://vod.bytedanceapi.com', params, data)
    print(rsp.text)
