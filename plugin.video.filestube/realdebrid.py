# -*- coding: utf-8 -*-
# dydrmntion@gmail.com


import requests
from cookielib import CookieJar


class Api(object):
    base_url = 'http://real-debrid.com/ajax'
    def __init__(self, user, password, persistent_cookie=False):
        self.user = user
        self.password = password

    def get_cookies(self):
        req = requests.get(self.base_url + '/login.php', params={
            'user': self.user,
            'pass': self.password})
        if req.ok and not req.json()['error']:
            return req.cookies

    def unrestrict_link(self, link):
        req = requests.get(self.base_url + '/unrestrict.php', params={
            'link': link}, cookies=self.get_cookies())
        if req.ok and not req.json()['error']:
            return req.json()['main_link']


def unrestrict_link(link, user, password):
    api = Api(user, password)
    return api.unrestrict_link(link)
