#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import lbindex
from lbdaemon import Daemon
import config
from requests.exceptions import *
import traceback
import sys

config.set_config()

# Set up log configurations
logger = logging.getLogger("LBIndex")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(config.LOGFILE_PATH)
handler.setFormatter(formatter)
logger.addHandler(handler)

class LBIndex(Daemon):
    """ Light Base Golden Extractor Daemon
    """
    def run(self):
        while True:
            try:
                lbindex.main()
            except (ConnectionError, Timeout) as e:
                logger.error('Não foi possivel estabelecer conexão com o servidor! ' + config.REST_URL)
            except Exception as e:
                logger.critical('UNCAUGHT EXCEPTION : %s' % traceback.format_exc())
                sys.exit(1)

if __name__ == "__main__":

    daemon = LBIndex(config.PIDFILE_PATH)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('starting daemon ...')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
            print('daemon stopped!')
        elif 'restart' == sys.argv[1]:
            daemon.restart()
            print('daemon restarted!')
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
