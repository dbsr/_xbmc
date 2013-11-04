# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

_cur_ctx = []


def get_cur_ctx():
    if _cur_ctx:
        return _cur_ctx[0]
