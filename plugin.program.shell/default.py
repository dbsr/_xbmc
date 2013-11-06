# -*- coding: utf-8 -*-
# dydrmntion@gmail.com

import os
import sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_here, 'resources/lib'))
import os
import contextlib
from cStringIO import StringIO
try:
    import simplejson as json
except ImportError:
    import json

from _addon import Addon

addon = Addon('plugin.program.shell')


HISTORY_FPATH = '/tmp/xbmc.script.shell~'


@contextlib.contextmanager
def pseudo_stdout(stdout=None):
    tmp = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = tmp


def get_history():
    try:
        with open(HISTORY_FPATH) as f:
            return json.load(f)
    except IOError:
        return []


def save_history(lines):
    with open(HISTORY_FPATH, 'w') as f:
        json.dump(lines, f)


def execute_line(line):
    if line[0] == '!':
        lines = [line[1:]]
    else:
        lines = get_history() + [line]
    with pseudo_stdout() as stdout:
        for l in lines:
            try:
                exec l
            except Exception as error:
               print "Traceback:\n > {!r}, line  {}\n{}: {}".format(
                       l, len(lines), repr(error).split('(')[0], error)
        if not locals().get('error'):
            save_history(lines)
    print "\n_______________STDOUT FOR LAST COMMAND_______________\n"
    print stdout.getvalue()
    print "\n_____________________________________________________\n"


def _exe(line):
    try:
        exec line
    except Exception as e:
        return e


@addon.route('/')
def index():
    addon.add_directory(addon.queries_for('.input'), {'title': '$: _'})
    addon.end_of_directory()

@addon.route('/input')
def input():
    addon.show_search_dialog('input', lambda line: execute_line(line), False)



addon.run(sys.argv)
