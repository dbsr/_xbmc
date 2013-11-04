# -*- coding: utf-8 -*-
# dydrmntion@gmail.com


def encode_response(resp):
    if isinstance(resp, dict):
        for k, v in resp.items():
            resp[k] = encode_response(v)
    elif isinstance(resp, list):
        resp = [encode_response(x) for x in resp]
    elif isinstance(resp, int) or isinstance(resp, float):
        resp = resp
    elif resp:
        if isinstance(resp, unicode):
            resp = resp.encode('utf8')
        elif isinstance(resp, str):
            resp = unicode(resp.decode('utf8'))
    return resp
