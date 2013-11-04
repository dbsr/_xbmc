# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import re

import requests

from _addon import cached

mock_settings = {
    'newznab_url': 'http://www.usenet-crawler.com',
    'api_key': 'a0a2ca0feaa180cc094872a5c2eb59ad'
}

REGEX_CATEGORIES_EXCLUDE = r'console|audio|pc|books|other'

class NewznabBaseException(Exception):
    pass


class NewznabParseError(NewznabBaseException):
    pass


def raise_if_parse_error(f):
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except KeyError:
            raise NewznabParseError('could not parse json data from api request')
    return wrapper

class Api(object):
    def __init__(self, newznab_url, api_key):
        self.base_url = 'http://' + newznab_url.rstrip('/').lstrip('http://')
        self.api_key = api_key

    @cached('newznab.cache')
    def get_categories(self):
        categories = []
        req = self._req({'t': 'caps'})
        for category in req['categories']['category']:
            if re.match(REGEX_CATEGORIES_EXCLUDE, category['@attributes']['name'], re.I):
                continue
            c = {
                'title': category['@attributes']['name'],
                'id': category['@attributes']['id'],
                'sub_categories': []
            }
            for subcat in category['subcat']:
                c['sub_categories'].append({
                    'title': subcat['@attributes']['name'],
                    'id': subcat['@attributes']['id']
                })
            categories.append(c)
        return categories

    def _search(self, params):
        params.update({'t': 'search', 'extended': 1})
        resp = self._req(params)
        return self.parse_search_results(resp)

    def parse_search_results(self, response):
        results = []
        for result in response['channel']['item']:
            result.update({
                'title': result['title'],
                'url': result['link']
            })
            results.append(result)
        attributes = response['channel']['response']['@attributes']
        total = attributes['total']
        offset = int(attributes['offset']) + len(results)
        if offset < int(total):
            next = offset
        else:
            next = None
        return results, next

    def custom_search(self, query):
        params = {
            'q': query,
            'cat': ','.join(x['id'] for x in self.get_categories)
        }
        return self._search(params)

    @cached('newznab.cache', 500)
    def list_category(self, category_id, offset=0):
        params = {
            'cat': category_id,
            'offset': offset
        }
        return self._search(params)

    def _req(self, params):
        url = self.base_url + '/api'
        params.update({
            'apikey': self.api_key,
            'o': 'json'
        })
        req = requests.get(url, params=params)
        try:
            return req.json()
        except:
            print req.content, req.status_code, req.url


    @cached('newznab.cache', 500)
    def movie_search(self, imdb_id):
        params = {
            't': 'movie',
            'imdbid': imdb_id
        }
        resp = self._req(params)
        return self.parse_search_results(resp)





