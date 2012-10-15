# -*- coding: utf-8 -*-
'''
Created on 03.10.2012

@author: unax
'''
from config import DEBUG
from message import (
    MessageTransfer,
    MessageType,
)

class AnyOperations(object):
    prio = 1000
    msg  = None
    meta = None
    msg_new = None

    def __init__(self, *args, **kwargs):
        self.msg = kwargs.get('msg')
        self.meta = kwargs.get('meta')
    @property
    def complete(self):
        return True
    @property
    def answer(self):
        return None
    @property
    def new_message(self):
        return self.msg_new
    @property
    def has_new_message(self):
        return isinstance(self.msg_new, MessageTransfer)

class UnknownOperations(AnyOperations):
    prio = 100
    def __init__(self, *args, **kwargs):
        super(UnknownOperations, self).__init__(self, *args, **kwargs)
    @property
    def complete(self):
        return True
    @property
    def answer(self):
        if DEBUG and self.msg.type not in [ MessageType.output, MessageType.regme ]:
            return [MessageTransfer(who=self.msg.who, body='unknown command', type=MessageType.output), ]

class DeterminateOperations(AnyOperations):
    prio = 0
    def __init__(self, *args, **kwargs):
        super(DeterminateOperations, self).__init__(self, *args, **kwargs)
        if 'regme' in self.msg.body:
            self.msg_new = MessageTransfer(who=self.msg.who,
                                           body='Hi, you on the mailing list! :)',
                                           type=MessageType.regme)
        elif 'hello' in self.msg.body:
            self.msg_new = MessageTransfer(who=self.msg.who,
                                           body='Hello, what do you need?',
                                           type=MessageType.hello)

    @property
    def complete(self):
        return False
    @property
    def answer(self):
        return None

class AddUserOperations(AnyOperations):
    prio = 1
    def __init__(self, *args, **kwargs):
        super(AddUserOperations, self).__init__(self, *args, **kwargs)
    @property
    def complete(self):
        return self.msg.type == MessageType.regme
    @property
    def answer(self):
        return [MessageTransfer(who=self.msg.who, body='hi!',
                                type=MessageType.output,
                                destination=1 ),
                MessageTransfer(who=self.msg.who, body='Hi, you on the my mailing list! :)',
                                type=MessageType.output), ]

class HelloOperations(AnyOperations):
    prio = 99
    def __init__(self, *args, **kwargs):
        super(HelloOperations, self).__init__(self, *args, **kwargs)
    @property
    def complete(self):
        return self.msg.type == MessageType.hello
    @property
    def answer(self):
        return [MessageTransfer(who=self.msg.who, body='Hello, what do you need?', type=MessageType.output), ]
