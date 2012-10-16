# -*- coding: utf-8 -*-
'''
Created on 15.10.2012

@author: unax
'''
from logging import Handler
import traceback
from sender import JabberSender
from datetime import datetime

def data_str_view(obj):
    res = u""
    if isinstance(obj, dict):
        for k in obj:
            o = data_str_view(obj.get(k))
            if o:
                res += u"    %s : %s\n" % (k, o)
    elif isinstance(obj, (str, unicode)):
        res += u"%s" % obj
    elif isinstance(obj, (tuple, list)):
        res += u"[%s]" % u",".join( filter(lambda x: x is not None,
                                           [ data_str_view(o) for o in obj  ]) )
    if len(res)<1: return None
    else:          return res

class Logger(Handler):
    sender = None
    __whoami = None

    def __init__(self, **kwargs):
        Handler.__init__(self)
        self.__whoami = kwargs.get('from')
        if not self.__whoami:
            self.__whoami = 'Djanbber Django Logger'
        self.sender = JabberSender.create(**kwargs)

    def request_view(self, record):
        if record.request: 
            request = record.request
            attrs = [ atr for atr in dir(request) if not('_' == atr[0]) ]
            request_repr = u""
            for atr in attrs:
                obj = getattr(request, atr, None)
                if isinstance(obj, (tuple, list, dict, str, unicode)):
                    request_repr += u"%s : %s\n" % (atr, data_str_view(obj))
        else:
            request_repr = 'No request'
        return request_repr

    def emit(self, record):
        if record.exc_info:
            stack_trace = u'\n'.join(traceback.format_exception(*record.exc_info))
        else:
            stack_trace = u'No stack trace available'
        message = u"%s\n========== %s %s ==========\n%s\n\n%s" %\
            (record.getMessage(),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             self.__whoami,
             stack_trace,
             self.request_view(record))
        self.sender.send(message)
