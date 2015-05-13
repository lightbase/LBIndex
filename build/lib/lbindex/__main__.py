#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler
from lbindex import index_registries
from lbindex import create_index
from lbdaemon import Daemon
from lbrest import LBRest
from multiprocessing import Pool
import config
import sys

config.set_config()

# Set up log configurations
logger = logging.getLogger("LBIndex")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler = logging.FileHandler(config.LOGFILE_PATH)
max_bytes = 1024*1024*20 # 20 MB
handler = RotatingFileHandler(config.LOGFILE_PATH, maxBytes=max_bytes, backupCount=10, encoding=None)
handler.setFormatter(formatter)
logger.addHandler(handler)


class LBIndex(Daemon):
    """ Light Base Golden Extractor Daemon
    """

    def run(self):
        """ 
        Overrided method used by super class.
        Crates a process pool object which controls a pool of worker processes.
        It supports asynchronous results with timeouts and callbacks and has a parallel map implementation.
        That means each base will be processed at same time.
        """
        lbrest = LBRest()
        self.is_running = False
        while not self.is_running:
            bases = lbrest.get_bases()
            if bases:
                self.is_running = True
                try:
                    pool = Pool(processes=len(bases))
                    logger.info('## STARTING LBINDEX PROCESS ##')
                    pool.map(index_registries, bases)
                except Exception as e:
                    logger.critical(str(e))

    @staticmethod
    def index():
        """
        Cria índice para todas as bases
        """
        lbrest = LBRest()
        bases_list = lbrest.get_bases()
        for base in bases_list:
            create_index(base)


if __name__ == "__main__":

    daemon = LBIndex(config.PIDFILE_PATH)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('starting daemon ...')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print('stopping daemon ...')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print('restarting daemon ...')
            daemon.restart()
        elif 'index' == sys.argv[1]:
            print("Atualizando índice para as bases...")
            daemon.index()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
