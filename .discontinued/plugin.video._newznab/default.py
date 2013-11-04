# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import sys
import os
import urllib
import time
import math

import requests
import xbmc
import xbmcgui
import xbmcplugin

from _addon import Addon
from newznab import Api
import metadata
import common

PNEUMATIC = "plugin://plugin.program.pneumatic"

# dev mock settings
mock_settings = {
    'newznab_url': 'http://www.usenet-crawler.com',
    'newznab_key': 'a0a2ca0feaa180cc094872a5c2eb59ad'
}
addon = Addon(common.ADDON_ID, mock_settings=mock_settings)
api = Api(addon.get_setting('newznab_url'), addon.get_setting('newznab_key'))

@addon.route('/')
def index():
    for category in api.get_categories():
        addon.add_directory(addon.queries_for('.category', category_id=category['id']),
                            {'title': category['title']})
        for subcat in category['sub_categories']:
            addon.add_directory(addon.queries_for('.category', category_id=subcat['id']),
                                {'title': '> {}'.format(subcat['title'])})
    addon.end_of_directory()


@addon.route('movie')
def movie(imdb_id):
    results, _ = api.movie_search(imdb_id)
    add_results(results)

    
@addon.route('category')
def category(category_id, offset=0, skip_ids=''):
    main_cat = int(math.floor(int(category_id) / 1000) * 1000)
    if main_cat == common.CATEGORY_MOVIES:
        list_movies(category_id, offset, skip_ids)


def list_movies(category_id, offset=0, skip_ids=None):
    results, next = api.list_category(category_id, offset)
    unique_ids = []
    if not skip_ids:
        skip_ids = ''
    skip_ids = [int(x) for x in skip_ids.split(',') if x]
    for result in results:
        labels = metadata.create_listitem(result)
        imdb_id = labels.get('code')
        if not imdb_id or imdb_id in skip_ids + unique_ids:
            continue
        unique_ids.append(imdb_id)
        addon.add_directory(addon.queries_for('.movie', imdb_id=imdb_id),
                labels, img=labels.get('cover'))
    if next:
        addon.add_directory(addon.queries_for('.category', 
            category_id=category_id, skip_ids=','.join(str(x) for x in skip_ids + unique_ids),
            offset=next), {'title': 'NExT'})
    addon.end_of_directory()



def add_results(results, next=None):
    for result in results:
        attributes = metadata.get_result_attributes(result)
        url = '{}?mode=play&nzb={}&nzbname={}&search_url=0'.format(
            PNEUMATIC, urllib.quote(result['url']), result['title'])
        listitem = xbmcgui.ListItem(result['title'])
        listitem.setInfo('video', {'title': result['title'], 'size': attributes.get('size')})
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(addon.handle, url, listitem)
    addon.end_of_directory()


if __name__ == '__main__':
    addon.run(sys.argv)
