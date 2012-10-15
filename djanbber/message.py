# -*- coding: utf-8 -*-
'''
Created on 02.10.2012

@author: unax
'''

class MessageType:
    input = 1
    output = 2
    regme = 3
    hello = 4
    unknown = 10

OUT_DESTINATION_TYPES = ('message', 'subscribe')

class MessageTransfer(object):
    __content = None
    def __init__(self, *args, **kwargs):
        self.__content = kwargs
    @property
    def type(self):
        return int(self.__content.get('type'))
    @property    
    def body(self):
        return unicode(self.__content.get('body'))
    @property    
    def who(self):
        return unicode(self.__content.get('who'))
    @property
    def destination(self):
        try:
            return OUT_DESTINATION_TYPES[int(self.__content.get('destination'))]
        except:
            return OUT_DESTINATION_TYPES[0]
