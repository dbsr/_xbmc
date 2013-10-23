# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import time
import json
import os

from ctx import get_cur_ctx


class cached(object):
    NO_EXPIRE = -1

    def __init__(self, cache_fpath, expires_after=None, kwargs_key=None):
        '''a memoize (cache) decorator

        :expires_after: time in seconds after cached entry expires.
        '''
        if not expires_after:
            expires_after = self.NO_EXPIRE
        self.expires_after = expires_after
        self.cache_fpath = cache_fpath
        self.kwargs_key = kwargs_key

    def __call__(self, f):
        ''' the decorator logic uses the hashed method / function name as 
        main key. The hashed arguments as subkeys. If found and age < expires_after
        returns cached entry.

        '''
        self.fhash = unicode(hash(f.__name__))
        def wrapped(*args, **kwargs):
            ctx = get_cur_ctx()
            if ctx:
                self.cache_fpath = os.path.join(ctx.get_profile(), 
                                                os.path.basename(self.cache_fpath))

            print self.cache_fpath
            _self = None
            if self.kwargs_key:
                hkey = kwargs.get(self.kwargs_key)
                if not kwargs.get(self.kwargs_key):
                    raise KeyError('could not find hkey in kwargs: {}'.format(
                        repr(kwargs)))
                hkey = unicode(hkey)
            else:
                if hasattr(args[0], f.__name__):
                    _self = args[0]
                    args = args[1:]
                hkey = unicode(hash(args))
            r = self.cache.get(self.fhash, {}).get(hkey)
            if r:
                ret, ts = r
                if time.time() - ts < self.expires_after or self.expires_after is self.NO_EXPIRE:
                    return ret
            if _self:
                ret = f(_self, *args, **kwargs)
            else:
                ret = f(*args, **kwargs)
            self.save(hkey, ret)
            return ret
        return wrapped
    
    @property
    def cache(self):
        try:
            with open(self.cache_fpath) as jsonfile:
                cache = json.load(jsonfile)
        except (ValueError, IOError):
            cache = {}
        return cache

    def save(self, arg_hash, val):
        ncache = self.cache
        v = [val, time.time()]
        if not ncache.get(self.fhash):
            ncache[self.fhash] = {}
        ncache[self.fhash][arg_hash] = v
        with open(self.cache_fpath, 'w') as jsonfile:
            json.dump(ncache, jsonfile)
