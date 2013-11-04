# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import requests


def get_tvshow_data(title):
    params = {
        'title': title,
        'type': 'json',
        'plot': 'none',
        'episode': 1,
        'limit': 1,
        'mt': 'TVS',
    }
    req = requests.get('http://mymovieapi.com/', params=params)
    print req.url
    if req.ok:
        resp = req.json()
        episodes = resp[0]['episodes']
        return parse_episodes(episodes)



def parse_episodes(episodes):
    seasons = {}
    for episode in episodes:
        e = episode.get('episode')
        if not e:
            continue
        s = episode.get('season')
        if not s:
            continue
        title = episode.get('title')
        if not seasons.get(s):
            seasons[s] = []
        seasons[s].append((s, e, title))
    return seasons
