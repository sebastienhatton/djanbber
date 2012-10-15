# -*- coding: utf-8 -*-
'''
Created on 04.10.2012

@author: unax
'''

DEBUG = True

try:
    from django.conf import settings
    DEBUG = settings.DEBUG
except:
    pass

CONFIG_FILE = '/etc/djabber.conf'