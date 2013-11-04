# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import os
import sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_here, 'resources/lib'))
import re
from urlparse import urlparse

from _addon import Addon, cached
import xbmcgui
import xbmcplugin

import filestube
from realdebrid import unrestrict_link

addon = Addon('plugin.video.filestube')

@addon.route('/')
def index():
    addon.add_directory(addon.queries_for('.search'), {'title': 'Search Filestube..'})
    addon.add_directory(addon.queries_for('.settings'), {'title': 'Settings'})
    addon.end_of_directory()

@addon.route('/search')
def search():
    '''prompt user with search dialog, dispatch based on results'''
    addon.show_search_dialog('Search Filestube:', results_callback, True)


@addon.route('/settings')
def settings():
    addon.show_settings()


def results_callback(q):
    @cached('query.cache', 300 if addon.get_setting('cache_results') == 'true' else 0)
    def _cached_query(q):
        return filestube.query(q)
    results, next_page = _cached_query(q)
    list_results(results, next_page)


@addon.route('/next-page')
def next_page(url):
    @cached('query.cache', 300 if addon.get_setting('cache_results') == 'true' else 0)
    def _cached_page(url):
        return filestube.next_page(url)
    results, next_page = _cached_page(url)
    list_results(results, next_page)
 


def list_results(results, next_page=None):
    for result in results:
        title = '[{host}] {title}'.format(**result)
        listitem = xbmcgui.ListItem(
            label=title,
            label2=result['ext'],
        )
        listitem.setInfo('video', {
            'size': result['size'],
        })
        listitem.setProperty('isPlayable', 'true')
        xbmcplugin.addDirectoryItem(addon.handle, addon.build_plugin_url(
            addon.queries_for('.resolve', url=result['url'])), listitem)
    if next_page:
        addon.add_directory(addon.queries_for('.next_page', url=next_page),
                {'title': 'next page'})
    addon.end_of_directory()


@addon.route('/resolve')
def resolve(url):
    resolved = False
    hoster_url = filestube.resolve_url(url)
    if hoster_url:
        realdebrid_url = unrestrict_link(hoster_url, *map(addon.get_setting, ['user', 'password']))
        if realdebrid_url:
            resolved = realdebrid_url
    addon.resolve_url(resolved)


addon.run(sys.argv)
