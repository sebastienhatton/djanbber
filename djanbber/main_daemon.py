# -*- coding: utf-8 -*-
'''
Created on 26.09.2012

@author: unax
'''
from base_daemon import BasicDaemon

class DjanbberDaemon(BasicDaemon):
    __in_shell = None
    def __init__(self, function):
        BasicDaemon.__init__(self)
        self.pidfile = None
        self.stdout  = None
        if hasattr(function, '__call__'):
            self.main = function
        else:
            self.main = None
    
    @property
    def configs(self):
        return { 'log' : self.stdout, 'pid' : self.pidfile }

    @configs.setter
    def configs(self, value):
        if isinstance(value, dict):
            self.pidfile = value.get('pid')
            self.stdout = value.get('log')
            self.__in_shell = value.get('shell')
    
    def add_log(self, content):
        print content
    
    def start(self):
        return BasicDaemon.start(self, interactive=self.__in_shell)
