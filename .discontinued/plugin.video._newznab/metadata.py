# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import time
import json
import os
import re

import requests
from _addon import cached

import common
from util import encode_response


IMDB_API_BASE_URL = 'http://mymovieapi.com/'

def get_result_attributes(result):
    attributes = {}
    for attr in result['attr']:
        k = attr['@attributes']['name']
        v = attr['@attributes']['value']
        try:
            v = int(v)
        except ValueError:
            pass
        if attributes.get(k):
            if not isinstance(attributes[k], list):
                attributes[k] = [attributes[k]]
            attributes[k].append(v)
        else:
            attributes[k] = v
    return attributes

def create_listitem(result):
    attributes = get_result_attributes(result)
    if common.CATEGORY_MOVIES in attributes['category']:
        return get_movie_labels(result, attributes)


def get_movie_labels(result, attributes):
    md = {
        'title': re.sub(r'\s{2,}', ' ', result['title']).split('\n')[0].strip(),
        'size': int(attributes['size']),
        'code': attributes.get('imdb')
    }
    if md['code']:
        md_imdb = get_imdb('tt' + str(md['code']))
        if md_imdb:
            for k, v in [(lambda x: x.get('poster', {}).get('imdb'), 'cover'),
                         (lambda x: ', '.join(x.get('genres', [])), 'genre'),
                         (lambda x: u'{}\n\nrating: {}'.format(
                             x.get('plot_simple', ''), x.get('rating')), 'plot'),
                         (lambda x: x.get('year'), 'year'),
                         (lambda x: 
                             re.sub(r'\s{2,}', ' ', x.get('title', '')).split('\n')[0].strip(),
                             'title')]:
                md[v] = k(md_imdb)
    cover = md.get('cover', '')
    if cover is None:
        cover = ''
    labels = {
        'cover': cover
    }
    for k in ['title', 'plot', 'genre', 'size', 'year', 'code']:
        v = md.get(k)
        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError:
                pass
        labels[k] = v
    return labels


@cached('metadata.cache')
def get_imdb(imdb_id=None):
    params = {
        'id': imdb_id,
        'release': 'full'
    }
    resp = api_req(IMDB_API_BASE_URL, params=params)
    if not resp.get('code'):
        return encode_response(resp)

def api_req(url, resource='', params=None):
    req = requests.get(url + resource, params=params)
    try:
        return req.json()
    except:
        print 'api error: ' + req.url
