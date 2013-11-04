#script.module._addon
###partial rewrite of t0mm0's common addon routines
<br>
###thanks to
Most of the code here is a 1 on 1 copy from t0mm0's common module. I've added some features.
So most, if not all of the original modules functionality will still work. 


###que?
I am a big fan of the lightweight Python web framework [Flask](https://github.com/mitsuhiko/flask‎
). With this addon I've tried to implement a routing system for xbmc addon's based on Flask. 
I have also written a new cache implementation.


###routing example
```python
import sys

from _addon import Addon

addon = Addon('plugin.example.id')

# index, automatically called when there are no queries
@addon.route('/')
def index():
    # queries_for is like flask's url_for helper function. 
    # In this example it resolves / creates a correct xbmc uri for
    # the view function 'foo'.
    addon.add_directory(addon.queries_for('foo', id=1), {'title': 'goto id 1'})
    addon.end_of_directory()
   
# note: routes, except for the index/fallback route, do not have to start with '/'
@addon.route('/foo')
def foo(id):
    # ...
    
    
if __name__ == '__main__':
    # this will parse the sys.argv queries and dispatch the parsed result to the
    # correct view  function.
    addon.run(sys.argv)
```

###caching example
```python
from _addon import cached

# the first argument is the name of the cache file. The decorator will
# create a cached directory in the addon's profile directory and store 
# all cache files there.
# cached uses the function's name plus the values of its arguments to create
# an unique hash key. If it finds the entry in the cache it will intercept
# the original function call and return the cached result instead.
@cached('example.cache', expires_after=300)
def a_slow_api_call(api_argument):
    # .. api calls / parsing logic ..
    return result

```

###docs
tbd

###contact
you can find my email on my [github page](https://github.com/dbsr)


[@ github](https://github.com/dbsr/_xbmc/_addon)
