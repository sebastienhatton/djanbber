# -*- coding: utf-8 -*-
'''
Created on 26.09.2012

@author: unax
'''

import os
import atexit
import sys
import time
from signal import SIGTERM
from datetime import datetime

class BasicDaemon(object):
    def __init__(self):
        self.pidfile = 'pidfile.pid'
        self.stdin   = '/dev/null'
        self.stdout  = '/dev/null'
    
    @property
    def exists(self):
        return not(self.main    is None)and\
               not(self.pidfile is None)and\
               not(self.stdout  is None)
 
    def daemonize(self):
        pid = os.fork()
        if pid == 0:
            os.setsid()
            pid = os.fork()
            if pid == 0:
                os.chdir(".")
                os.umask(0)
            else:
                sys.exit(0)
        else:
            sys.exit(0)
 
        atexit.register(self.delpid)
 
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
        return pid
 
    def descriptors(self):
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
 
    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self,interactive=False):
        if interactive:
            print "Starting program in interactive mode"
            self.run()
            return
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
 
        if pid:
            message = "Daemon already running? (pid=%s)\n"
            sys.stderr.write(message % pid)
            sys.exit(1)
 
        pid = self.daemonize()
        print "Starting daemon."
        self.descriptors()
        self.run()
 
    def stop(self):
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
 
        if not pid:
            message = "Daemon not running? (check %s)\n"
            sys.stderr.write(message % self.pidfile)
            return
 
        print "Stopping daemon.\nWaiting for PID: %s" % pid
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
 
    def restart(self):
        self.stop()
        self.start()
 
    def main(self):
        print >> sys.stderr, "Reload BasicDaemon.main"
        print >> sys.stdout, "Reload BasicDaemon.main"
        sys.exit(1)
        
    def add_log(self, msg):
        print >> sys.stdout, ("[%s] %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

    def run(self):
        self.main()
