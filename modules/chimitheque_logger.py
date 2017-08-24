# -*- coding: utf-8; -*-
#
# (c) 2011-2015 Thomas Bellembois thomas.bellembois@ens-lyon.fr
#
# This file is part of Chimithèque.
#
# Chimithèque is free software; you can redistribute it and/or modify
# it under the terms of the Cecill as published by the CEA, CNRS and INRIA
# either version 2 of the License, or (at your option) any later version.
#
# Chimithèque is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the Cecill along with Chimithèque.
# If not, see <http://www.cecill.info/licences/>.
#
# SVN Revision:
# -------------
# $Id: db.py 222 2015-07-21 16:06:35Z tbellemb2 $
#
import logging
import sys
import os
from gluon import current
from gluon.html import XML
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

def LINE( back = 1 ):
    return sys._getframe( back + 1 ).f_lineno

def FILE( back = 1 ):
    return sys._getframe( back + 1 ).f_code.co_filename

def FUNC( back = 1):
    return sys._getframe( back + 1 ).f_code.co_name

class chimitheque_logger:

    def __init__(self):
        cache_opts = {
            'cache.type': 'memory',
            'cache.data_dir': './applications/chimitheque/cache/',
            'cache.lock_dir': './applications/chimitheque/cache/'
        }
        #cache_opts = {
        #    'cache.type': 'memory'
        #    'cache.type': 'file'
        #}
        cache = CacheManager(**parse_cache_config_options(cache_opts))
        # user id has a unique key to store the MESSAGE in cache
        try:
            uid = 'cache_console_%s' %str(current.auth.user.id)
        except AttributeError:
            uid = ''
        # getting the cache
        self.tmpl_cache = cache.get_cache(uid, expire=None)

        self.logger = logging.getLogger('web2py.app.chimitheque')

    def getLevel(self):
        return self.logger.getEffectiveLevel()

    def setLevel(self, level):
         self.logger.setLevel(level)

    def debug(self, filename=None, funcname=None, linenumber=None, message=''):
        _filename = FILE() if not filename else filename
        _filename = _filename.split(os.path.sep)[-1]
        _funcname = FUNC() if not funcname else funcname
        _linenumber = LINE() if not linenumber else linenumber
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('%s:%s:%s:%s' %(_filename, _funcname, _linenumber, message))
            #self.logger.debug('')

    def info(self, message=''):
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info(message)

    def warning(self, message=''):
        if self.logger.isEnabledFor(logging.WARNING):
            self.logger.warning(message)

    def error(self, message=''):
        if self.logger.isEnabledFor(logging.ERROR):
            self.logger.error(message)

    def critical(self, message=''):
        if self.logger.isEnabledFor(logging.CRITICAL):
            self.logger.critical(message)

    def get_cached_item(self, message, index):
        _message = self.tmpl_cache.get('console')
        if index == -2:
            index = len(_message) - 1
        if index > len(_message) - 1 or index == -1:
            _message.append(message)
        else:
            _message[ index ] = message
            _message = _message[0:index+1]
        self.tmpl_cache.put('console', _message)
        return _message

    def ram_clear(self):
        self.tmpl_cache.remove_value(key='console')

    def ram(self, message=None, index=0):
        # convert Lazy T into string
        message = str(message) if message else None
        # no MESSAGE = get the cached value
        if not message:
            return XML('<br/>'.join([m for m in self.tmpl_cache.get('console')])) if self.tmpl_cache.has_key('console') else ''
        # returning the cached item
        if self.tmpl_cache.has_key('console'):
            return self.tmpl_cache.get(key='console', createfunc=self.get_cached_item(message, index))
        else:
            return self.tmpl_cache.put('console', [ message ])
