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
import xbmc
#import urlresolver

import filestube
from realdebrid import unrestrict_link, RealDebridAuthError
from browser import Browser

addon = Addon('plugin.video.filestube')
b = Browser(addon.get_profile())

@addon.route('/')
def index():
    addon.add_directory(addon.queries_for('.search'), {'title': 'Search Filestube..'})
    addon.add_directory(addon.queries_for('.browser'), {'title': 'Browser'})
    addon.add_directory(addon.queries_for('.settings'), {'title': 'Settings'})
    addon.end_of_directory()

@addon.route('/search')
def search():
    '''prompt user with search dialog, dispatch based on results'''
    addon.show_search_dialog('Search Filestube:', query, True)


@addon.route('/settings')
def settings():
    addon.show_settings()

@addon.route('/query')
def query(q):
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
        addon.log('filestube :: hoster url found on url: {}'.format(url))
        if addon.get_setting('use_urlresolver') == 'true':
            # broken in gotham
            # resolved_url = urlresolver.resolve(hoster_url)
            pass
        else:
            try:
                resolved_url = unrestrict_link(hoster_url, *map(addon.get_setting, ['user', 'password']))
            except RealDebridAuthError as e:
                addon.show_error_dialog(['RealDebrid Auth Error:', e.message])
                resolved_url = None
            addon.log("resolved_url result: {}".format(resolved_url))
        if resolved_url:
            resolved = resolved_url
    addon.resolve_url(resolved)


@addon.route('/browser')
def browser():
    addon.add_directory(addon.queries_for('.browser_add'), {'title': 'add tvshow'})
    for title in b.data['tvshows'].keys():
        addon.add_directory(addon.queries_for('.browse', title=title), {
            'title': title})
    addon.end_of_directory()


@addon.route('/browser_add')
def browser_add():
    addon.show_search_dialog('Name of Show:', add_callback, False)


def add_callback(query):
    b.add_tvshow(query)


@addon.route('/browse')
def browse(title):
    tvshow_data = b.get_tvshow(title)
    for _, season in sorted(tvshow_data.items()):
        for s, e, etitle in sorted(season, key=lambda k: k[1]):
            t = 'S{}E{} | {}'.format(str(s).zfill(2), str(e).zfill(2), etitle)
            q = ' '.join(reversed([t.split('|')[0].strip(), title]))
            addon.add_directory(addon.queries_for('.query', q=q), {'title': t})
    addon.end_of_directory()

addon.run(sys.argv)
