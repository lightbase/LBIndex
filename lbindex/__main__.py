#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import getopt
# import argparse

import pkg_resources  # part of setuptools

import config
import logging
from logging.handlers import RotatingFileHandler

from lbdaemon import Daemon
from multiprocessing import Pool

from lbindex import index_registries
from lbrest import LBRest

config.set_config()

# NOTE: Set up log configurations! By Questor
logger = logging.getLogger("LBIndex")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '\
    '%(message)s')
max_bytes = 1024*1024*20 # 20 MB
handler = RotatingFileHandler(
    config.LOGFILE_PATH, 
    maxBytes=max_bytes, 
    backupCount=10, 
    encoding=None)
handler.setFormatter(formatter)
logger.addHandler(handler)


class LBIndex(Daemon):
    """LightBase extractor daemon."""

    def run(self):
        """ 
        Overrided method used by super class. Crates a process pool 
        object which controls a pool of worker processes. It supports 
        asynchronous results with timeouts and callbacks and has a 
        parallel map implementation. That means each base will be 
        processed at same time.
        """

        lbrest = LBRest()
        self.is_running = False
        while not self.is_running:

            # NOTE: Obtêm a lista de bases e as suas respectivas 
            # configurações de indexação quando houver! By Questor
            bases = lbrest.get_bases()
            bases_indexes = lbrest.get_index(bases)

            if bases_indexes:
                self.is_running = True
                try:
                    pool = Pool(processes=len(bases_indexes))
                    logger.info('## STARTING LBINDEX PROCESS ##')
                    pool.map(index_registries, bases_indexes)
                except Exception as e:
                    logger.critical(str(e))
            else:
                time.sleep(30)

    def cmd(self, opt):  
        """??????????????????????????????????"""

        print("COMMAND! COMMAND! COMMAND! COMMAND! COMMAND! COMMAND!")
        print(str(opt))
        print("COMMAND! COMMAND! COMMAND! COMMAND! COMMAND! COMMAND!")

    def status(self):
        """Check process is running."""

        # NOTE: Check for a pidfile to see if the daemon already runs!
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid is None:
            message = "pidfile {0} is not running. \n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)
        elif self.check_pid(pid):
            message = "pidfile {0} is running. \n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)
        else:
            message = "pidfile {0} is not running. \n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)

    def help(self):  
        """Exibir o help."""

        version = str(pkg_resources.require("lbindex")[0].version)
        print(
"""lbindex - LightBase Textual Index Service %s

usage: lbindex <start>                     Start the service
   or: lbindex <stop>                      Stop the service
   or: lbindex <restart>                   Restart the service
   or: lbindex <status>                    Get service status
   or: lbindex <index>                     Index/reindex indexable bases
   or: lbindex <help>                      Print Help (this message) and exit
   or: lbindex <cmd <-a|-h> [value]>       Pass specific commands

Arguments:
   -a  or  --action     Command to execute (need cmd arg)
   -h  or  --help       Print Help (this message) and exit (may need cmd arg)""" 
            % (version))

    # TODO: Estático por que? By Questor
    @staticmethod
    def index():
        """Cria índice para todas as bases."""

        lbrest = LBRest()
        bases_list = lbrest.get_bases()
        for base in bases_list:
            create_index(base)

if __name__ == "__main__":

    daemon = LBIndex(config.PIDFILE_PATH)

    # if len(sys.argv) == 2:
        # if 'start' == sys.argv[1]:

            # # NOTE: Start point! By Questor
            # print('starting daemon ...')
            # daemon.start()
        # elif 'stop' == sys.argv[1]:
            # print('stopping daemon ...')
            # daemon.stop()
        # elif 'restart' == sys.argv[1]:
            # print('restarting daemon ...')
            # daemon.restart()
        # elif 'status' == sys.argv[1]:
            # daemon.status()
        # elif 'index' == sys.argv[1]:
            # print("Atualizando índice para as bases...")
            # daemon.index()
        # else:
            # print "Unknown command"
            # sys.exit(2)
        # sys.exit(0)
    # else:
        # print("usage: %s start|stop|restart" % sys.argv[0])
        # sys.exit(2)

    if len(sys.argv) < 2:
        print("Missing arguments!")
        print("More info with: \"lbindex -h\"")
        sys.exit(2)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:

            # NOTE: Start point! By Questor
            print('Starting daemon ...')
            daemon.start()
            sys.exit(0)
        elif 'stop' == sys.argv[1]:
            print('Stopping daemon ...')
            daemon.stop()
            sys.exit(0)
        elif 'restart' == sys.argv[1]:
            print('Restarting daemon ...')
            daemon.restart()
            sys.exit(0)
        elif 'status' == sys.argv[1]:
            daemon.status()
            sys.exit(0)
        elif 'index' == sys.argv[1]:
            print("Atualizando índice para as bases...")
            daemon.index()
            sys.exit(0)
        elif 'help' == sys.argv[1]:
            daemon.help()
            sys.exit(0)
        elif 'run' == sys.argv[1]:
            print("Running daemon...")
            daemon.run()
            sys.exit(0)
        else:
            opts = []
            args = []
            try:
                opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
                if not opts:
                    raise getopt.GetoptError("")
                daemon.help()
            except getopt.GetoptError as e:
                print("Unknown option(s) and/or argument(s): \"" + 
                    str(sys.argv[1:]) + "\"")
                print("More info with: \"lbindex -h\"")
                sys.exit(2)

    if sys.argv[1] == 'cmd' and len(sys.argv) >= 3:
        opts = []
        args = []
        try:
            opts, args = getopt.getopt(sys.argv[2:], 'a:d:', ["action="])
            daemon.cmd(opts)
            sys.exit(0)
        except getopt.GetoptError as e:
            print("Unknown option argument(s): \"" + str(sys.argv[2:]) + "\"")
            print("More info with: \"lbindex -h\"")
            sys.exit(0)
            sys.exit(2)

    if len(sys.argv) >= 3:
        print("Invalid arguments!")
        print("More info with: \"lbindex -h\"")
        sys.exit(0)
        sys.exit(2)
