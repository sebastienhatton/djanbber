#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 29.09.2012

@author: unax
'''


from baker import Baker
from ConfigParser import SafeConfigParser
from djanbber.main_daemon import DjanbberDaemon
from djanbber.jabber_bot import DjanbberBot
from djanbber.config import CONFIG_FILE

parser = SafeConfigParser()
script_engine = Baker()
bot = DjanbberBot()
daemon = DjanbberDaemon(bot.run)
bot.logger = daemon.add_log

def options():
    return {'log'                : parser.get('options', 'log'),
            'pid'                : parser.get('options', 'pid'),
            'max_income_queue'   : parser.get('options', 'max_income_queue'),
            'max_outcome_queue'  : parser.get('options', 'max_outcome_queue') }

@script_engine.command
def start(config=CONFIG_FILE):
    parser.read(config)
    if not daemon.exists:
        daemon.configs = options()
        bot.parametrs(parser=parser)
        if not bot.connected and bot.connect():
            daemon.start()

@script_engine.command
def shell(config=CONFIG_FILE):
    try:
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
    except:
        raise Exception("Install ipython, he's a good")
    parser.read(config)
    if not daemon.exists:
        opt = options()
        opt['shell'] = True
        daemon.configs = opt
        bot.parametrs(parser=parser)
    ishell = InteractiveShellEmbed(user_ns={'daemon' : daemon, 'bot' : bot })
    ishell()

@script_engine.command
def stop(config=CONFIG_FILE):
    parser.read(config)
    if not daemon.exists:
        daemon.configs = options()
    if bot.alive:
        bot.disconnect()
    daemon.stop()

script_engine.run()
