About
========
:Info: Logger for Django and Flask projects, where messages coming through jabber-bot
:Author: Michael

Dependencies
========
- python-xmpp
- `Baker <http://pypi.python.org/pypi/Baker/1.1>`_
- `HotQueue <http://richardhenry.github.com/hotqueue/tutorial.html>`_

Message queue created by redis, this a not universal solution, but i use redis often, and for this project too.

Don't think this is bad ;)

How to use?

Copy package in you project. And copy robot start script in project directory.

If you use Django append 'djanbber' to INSTALLED_APPS,
and change logger configuration in django settings like this::

	LOGGING = {
	    'version': 1,
	    'disable_existing_loggers': False,
	    'filters': {
	        'require_debug_false': {
	            '()': 'django.utils.log.RequireDebugFalse'
	        }
	    },
	    'handlers': {
	        'mail_admins': {
	            'level': 'ERROR',
	            'filters': ['require_debug_false'],
	            'class': 'django.utils.log.AdminEmailHandler'
	        },
	        'djanbber': {
	            'level' : 'ERROR',
	            'from'  : 'test server',
	            'class' : 'djanbber.django.Logger',
	            'redis' : {
	                 'host' : 'localhost',
	                 'db'   : 2,
	                 'port' : 6379,
	            },
	            'recipients' : ( 'admin1@jabber.ru', 'admin2@jabber.ru', )
	        },
	    },
	    'loggers': {
	        'django.request': {
	            'handlers': ['mail_admins', 'djanbber'],
	            'level': 'ERROR',
	            'propagate': True,
	        },
	    }
	}

But more you must run jabber bot.
Jabber bot options place here on default /etc/djanbber.ini and contains such sections::

	[redis]
	host = localhost
	port = 6379
	db = 3
	[jabber]
	login = robotaccount@jabber.ru
	password = pass
	server = jabber.ru
	port = 5222
	lock_file = /tmp/jabber.runed
	status = djanbber ready
	users = admin1@jabber.ru, admin2@jabber.ru
	[options]
	max_income_queue = 2048
	max_outcome_queue = 16384
	pid = /tmp/djanbber.pid
	log = /var/log/djanbber.txt

How to run bot? So simple, use 'start' for script::

	#cd /data/web/project1/
	#./djanbber-bot.py start
	
	or
	
	#./djanbber-bot.py start --config /home/username/jabber.conf
	
	or you can use shell, and see log in console directly
	
	#./djanbber-bot.py shell
	Python 2.7.3rc2
	In [1]: daemon.start()

How to add bot in contact list?

If you has in djanbber.ini 'users', just append jabber account of bot in your contact list and say him 'regme', and he will ask to add self.

How send message from runtime?

If you create configuration for djanbber in django settings, you can use default sender::

	from djanbber.sender import JabberSender
	sender = JabberSender()
	sender.send(u'Hello! How are you?')

I will soon be testing module for flask..

Sincerely, Michael Vorotyntsev.