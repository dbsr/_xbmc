# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import requests
from BeautifulSoup import BeautifulSoup

base_url = 'http://www.filestube.com'
default_params = {
    'hosting': '23,99,15,24,13,22,27,25,8,28,2,40,11,46,47,51,55,59,60,64,65,67,68,70,71,81,87,92,97,102,104'
}

QUERY_SIZE_GREATER_THAN = '>'
QUERY_SIZE_LESSER_THAN = '<'
QUERY_EXTENSION_IS = '='


def _req(resource=None, params=None):
    if resource:
        url = base_url + "/" + resource
    else:
        url = base_url
    if params:
        params.update(default_params)
    else:
        params = {}
    req = requests.get(url, params=params)
    return BeautifulSoup(req.content)


def query(query):
    params = _parse_query(query)
    soup = _req('query.html', params)
    return parse_results(soup)

def _parse_query(query):
    qsplit = query.split()
    params = {
        'q': []
    }
    for i, q in enumerate(qsplit):
        if q[0] in [QUERY_SIZE_LESSER_THAN, QUERY_SIZE_GREATER_THAN, QUERY_EXTENSION_IS]:
            if q[0] is QUERY_SIZE_LESSER_THAN:
                k = 'sizeto'
            elif q[0] is QUERY_SIZE_GREATER_THAN:
                k = 'sizefrom'
            else:
                k = 'select'
            params[k] = q[1:]
        else:
            params['q'].append(q)
    params['q'] = ' '.join(params['q'])
    return params


def next_page(url):
    soup = _req(url)
    return parse_results(soup)

def parse_results(soup):
    results = []
    for result in soup.find('div', {'id': 'results'}).findAll('div', {'id': 'newresult'}):
        r = {
            'title': result.find('a').text.strip(),
            'url': result.find('a').get('href')
        }
        metadatas = [('host', lambda x: x), 
                     ('ext', lambda x: x.strip('ext:')), 
                     ('size', lambda x: x)]
        valid_result = True
        for m in [v for v in result.find('div', {'style': 'overflow: hidden'})
                  .text.split('&nbsp;') if v]:
            if not metadatas:
                continue
            k, l = metadatas.pop(0)
            v = l(m.strip()).strip()
            if k == 'size':
                if 'parts' in v:
                    valid_result = False
                else:
                    v = int(v.split()[0].strip()) * (1024 ** 2)
            r[k] = v
        if valid_result:
            results.append(r)
    next_page = filter(
            lambda a: a.text == 'Next', 
            soup.findAll('a', {'rel': 'nofollow next'}))
    if next_page:
        next_page = next_page[0].get('href')
    
    return results, next_page

def resolve_url(url):
    soup = _req(url)
    return soup.pre.text.strip()

