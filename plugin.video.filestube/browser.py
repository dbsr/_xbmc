# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import os
import json

import imdb_api


class Browser(object):
    def __init__(self, addon_data_path):
        self.data_path = os.path.join(addon_data_path, 'browser.data')
        self.data = self.get_persistent_data()

    def get_persistent_data(self):
        try:
            with open(self.data_path) as f:
                return json.load(f)
        except IOError:
            return {'tvshows': {}}

    def save_persistent_data(self):
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f)

    def add_tvshow(self, title):
        self.data['tvshows'][title] = -1
        self.save_persistent_data()

    def rename_tvshow(self, old_title, new_title):
        self.data['tvshows'][new_title] = self.data['tvshows'][old_title].pop()


    def get_tvshow(self, title):
        if self.data['tvshows'].get(title) == -1:
            self.data['tvshows'][title] = imdb_api.get_tvshow_data(title)
        return self.data['tvshows'][title]

    def delete_tvshow(self, title):
        try:
            del self.data['tvshows'][title]
        except KeyError:
            pass


