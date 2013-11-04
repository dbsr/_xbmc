# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import re

import requests


class RealDebridAuthError(Exception):
    pass

class Api(object):
    base_url = 'http://real-debrid.com/ajax'
    def __init__(self, user, password, persistent_cookie=False):
        self.user = user
        self.password = password
        if len(self.user) == 0 or len(self.password) == 0:
            raise RealDebridAuthError('Invalid login settings')

    def get_cookies(self):
        req = requests.get(self.base_url + '/login.php', params={
            'user': self.user,
            'pass': self.password})
        if req.ok:
            resp = req.json()
            if not resp['error']:
                return req.cookies
            emessage = re.sub(r'\s+|\n', ' ', resp['message'])
            raise RealDebridAuthError(emessage)

    def unrestrict_link(self, link):
        req = requests.get(self.base_url + '/unrestrict.php', params={
            'link': link}, cookies=self.get_cookies())
        if req.ok and not req.json()['error']:
            return req.json()['main_link']


def unrestrict_link(link, user, password):
    api = Api(user, password)
    return api.unrestrict_link(link)
