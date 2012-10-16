# -*- coding: utf-8 -*-
'''
Created on 16.10.2012

@author: unax
'''

import logging
from logging import Handler
from sender import JabberSender

class JabberLogger(Handler):
    def init__(self, **kwargs):
        level = kwargs.get('level')
        if not level:
            level = logging.ERROR
        Handler.__init__(self, level=level)
        self.__whoami = kwargs.get('from')
        if not self.__whoami:
            self.__whoami = 'Djanbber Flask Logger'
        self.sender = JabberSender.create(**kwargs)

    def emit(self, record):
        self.sender.send( unicode(record) )
