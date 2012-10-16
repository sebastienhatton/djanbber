# -*- coding: utf-8 -*-
'''
Created on 29.09.2012

@author: unax
'''

ITER_INTERVAL = 1
ACCELERATION = 2

import os
from time import sleep as time_delay
import xmpp
import weakref
from ConfigParser import SafeConfigParser
from datetime import datetime
from hotqueue import HotQueue
from threading import Thread
from message import (
    MessageTransfer,
    MessageType,
)
import answers
import inspect

operations = sorted([ op[1] for op in  inspect.getmembers(answers, inspect.isclass)
                            if issubclass(op[1], answers.AnyOperations) ],
                    key=lambda op: op.prio )

class HandlerThread(Thread):
    __active = True
    __meta   = None
    __logger = None
    __input_queue_ref  = None
    __output_queue_ref = None

    def __init__(self, **kwargs):
        self.__active = True
        self.__meta = kwargs.get('meta')
        if hasattr(kwargs.get('logger'), '__call__'):
            self.__logger = kwargs.get('logger')
        else:
            self.__logger = lambda x: None 
        
        self.__input_queue_ref = kwargs.get('input_queue')
        self.__output_queue_ref = kwargs.get('output_queue')
        super(HandlerThread, self).__init__()

    def run(self):
        dt = float(ITER_INTERVAL)/float(ACCELERATION)
        input_queue = self.__input_queue_ref
        while self.__active:
            time_delay(dt)

            if isinstance(input_queue, HotQueue):
                m = input_queue.get()
                if isinstance(m, MessageTransfer):
                    answer_messages = None
                    for operation in operations:
                        op_result = operation(msg=m, meta=self.__meta)
                        if op_result.complete:
                            answer_messages = op_result.answer
                            break
                        if op_result.has_new_message:
                            m = op_result.new_message

                    if isinstance(answer_messages, list):
                        for am in answer_messages:
                            self.__output_queue_ref.put(am)
            else:
                self.__logger('%s: queue no exist' % self.__class__.__name__)

    def stop(self):
        self.__active = False

def message_sender(message, connection):
    if connection and isinstance(message, MessageTransfer):
        try:
            msg = xmpp.protocol.Message(message.who, message.body, "chat")
            connection.send(msg)
            return True
        except:
            pass
    return False

def subscribe_sender(message, connection):
    if connection and isinstance(message, MessageTransfer):
        try:
            connection.send(xmpp.Presence(to=message.who, typ = 'subscribe'))
            connection.send(xmpp.Presence(to=message.who, typ = 'subscribed'))
            return True
        except:
            pass
    return False

SENDER_METHOD = {
    'message'   : message_sender,
    'subscribe' : subscribe_sender
}

class DjanbberBot(object):
    __parametrs = None
    __main_logger = None
    __input_queue = None
    __output_queue = None
    __xmpp_connection = None
    __input_queue  = None
    __output_queue = None
    __users = None

    def __init__(self, *args, **kwargs):
        self.parametrs(**kwargs)

    @property
    def connected(self):
        return self.__xmpp_connection and not(self.__xmpp_connection() is None)

    @property
    def alive(self):
        return self.__parametrs and\
               os.path.exists(self.__parametrs.get('lock_file'))

    def parametrs(self, **kwargs):
        if isinstance(kwargs.get('parser'), SafeConfigParser):
            parser = kwargs.get('parser')
            self.__parametrs = {'login'    : parser.get('jabber', 'login'),
                                'password' : parser.get('jabber', 'password'),
                                'server'   : parser.get('jabber', 'server'),
                                'port'     : parser.get('jabber', 'port'),
                                'lock_file': parser.get('jabber', 'lock_file'),
                                'status'   : parser.get('jabber', 'status') }
            redis = {'host' : parser.get('redis', 'host'),
                     'db'   : parser.get('redis', 'db'),
                     'port' : int(parser.get('redis', 'port')) }
            self.__input_queue  = HotQueue('djanbber_input_queue', **redis)
            self.__output_queue = HotQueue('djanbber_output_queue',**redis)
            self.__users = [ user.strip() for user in parser.get('jabber', 'users') ]

    def connect(self):
        jid = xmpp.protocol.JID(self.__parametrs.get('login'))
        conn = xmpp.Client(self.__parametrs.get('server'), debug=[])
        conres = conn.connect((self.__parametrs.get('server'),
                               self.__parametrs.get('port')))
        authres = conn.auth(jid.getNode(),
                            self.__parametrs.get('password'))

        if authres is not None:
            self.__xmpp_connection = weakref.ref(conn)
        else:
            self.add_log('Error: jabber connection failed.')
            return False

        conn.RegisterHandler('presence', self.status_handler)
        conn.RegisterHandler('message', self.message_handler)
        conn.sendInitPresence()
        presence = xmpp.Presence(status=self.__parametrs.get('status'),
                                 show='chat',
                                 priority='1')
        conn.send(presence)
        conn.online = 1
        f = open(self.__parametrs.get('lock_file'), 'w')
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.close()
        return True

    def message_handler(self, con, msg):
        content = msg.getBody()
        if content:
            who = str(msg.getFrom()).split('/', 1)
            m = MessageTransfer(body = unicode(content)[0:128],
                                who = who[0],
                                type = MessageType.input)
            if isinstance(self.__input_queue, HotQueue):
                self.__input_queue.put(m)
            else:
                self.add_log('Error: queue no exist, check redis configuration.')

    def status_handler(self, con, msg):
        pass

    def __send_handler(self):
        if isinstance(self.__output_queue, HotQueue):
            new_message = self.__output_queue.get()
        else:
            self.add_log('Error: outcome queue no exist, check redis configuration.')
        if isinstance(new_message, MessageTransfer) and MessageType.is_output(new_message.type):
            SENDER_METHOD[new_message.destination](new_message, self.__xmpp_connection())

    def run(self):
        conn = self.__xmpp_connection()
        if conn:
            handler_thread = HandlerThread(logger = self.add_log,
                                           input_queue  = self.__input_queue,
                                           output_queue = self.__output_queue,
                                           meta = {'users' : self.users })
            handler_thread.setDaemon(True)
            handler_thread.start()
            
            while self.alive:
                conn.Process(ITER_INTERVAL)
                self.__send_handler()
            conn.disconnect()
            handler_thread.stop()

    def disconnect(self):
        if self.__parametrs:
            os.remove(self.__parametrs.get('lock_file'))
    
    def send_message(self, **kwargs):
        kwargs['type'] = MessageType.output
        kwargs['destination'] = 0
        self.__output_queue.put(MessageTransfer(**kwargs))

    @property
    def users(self):
        return self.__users

    @property
    def logger(self):
        return self.__main_logger is not None
    
    @logger.setter
    def logger(self, function):
        if hasattr(function, '__call__'):
            self.__main_logger = function
        
    def add_log(self, text):
        if self.__main_logger and text:
            self.__main_logger(text)
