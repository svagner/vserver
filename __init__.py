#!/usr/bin/env python
import argparse, daemon, os
import lockfile 
from HTTP import HTTPServer

__author__ = "Stan Putrya"
__copyright__ = "Copyright (C) 2014 Stan E. Putrya"

__revision__ = "$Id$"
__version__ = "0.1"




class App(object):
    def __init__(self):
        # overridable options
        self.PID_FILE = "/var/run/VServer.pid"
        self.LOG_FILE = "/var/log/VServer.log"
        self.WORKDIR = os.getcwd()
        self.UMASK = 0        
    def run(self): 
        http = HTTPServer()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--daemon', action='store_true', default=False, help='Run as daemon')
    arg_parser.add_argument('--cwd', action='store', default='/', 
                            help='Full path of the working directory to which the process should change on daemon start.')
    arg_parser.add_argument('--uid', action='store', type=int, default=os.getuid(),
        help='The user ID ("UID") value and group ID ("GID") value to switch the process to on daemon start.')
    arg_parser.add_argument('--logfile', action='store', default='/var/log/vserver.log',
            help='The daemon\'s log file.')    
    arg_parser.add_argument('--pidfile', action='store', default='/var/run/vserver.pid',
                help='The daemon\'s pid file.')    
    args = vars(arg_parser.parse_args())
    Application = App()
    if args['daemon']:
        logfile = open(args['logfile'], "w+")
        context = daemon.DaemonContext(working_directory=args['cwd'], stdout=logfile, stderr=logfile, pidfile=lockfile.FileLock(args['pidfile']), uid=args['uid'])
        with context:
            Application.run()           
    else:
        Application.run()           
