# -*- coding: utf-8 -*-
'''
Created on 15.10.2012

@author: unax
'''

from message import MessageTransfer, MessageType
from hotqueue import HotQueue

class JabberSender(object):
    __this = None
    __output_queue = None
    __conf = None

    def __new__(cls):
        if cls.__this is None:
            cls.__this = super(JabberSender, cls).__new__(cls)
        return cls.__this

    @classmethod
    def create(cls, **conf):
        if isinstance(conf, dict) and len(conf)>1 and cls.__conf is None:
            cls.__conf = {}
            redis = conf.get('redis')
            if isinstance(redis, dict):
                cls.__output_queue = HotQueue('djanbber_output_queue',**redis)
            else:
                raise Exception("You doesn't set configuration for redis connection! Check it.")
            
            recipients = conf.get('recipients')
            if isinstance(recipients, (list, tuple)) and recipients:
                cls.__conf['recipients'] = [ r for r in recipients if isinstance(r, (str, unicode)) ]
            else:
                raise Exception("Set list of recipients in configuration. A bot can't send messages.")
        return cls()

    def send(self, message):
        if isinstance(message, (str, unicode)) and len(message)>0 and self.__conf: 
            for user in self.__conf.get('recipients'):
                msg = MessageTransfer(type = MessageType.output,
                                      body = message,
                                      who = user )
                self.__output_queue.put(msg)
