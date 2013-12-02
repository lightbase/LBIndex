#!/usr/bin/python
# -*- coding: utf-8 -*-

from daemon import runner
import logging
import time
import lbindex
import config
config.set_config()

class App():
   
    def __init__(self):
        self.stdin_path = config.STDIN_PATH
        self.stdout_path = config.STDOUT_PATH
        self.stderr_path = config.STDERR_PATH
        self.pidfile_path = config.PIDFILE_PATH
        self.pidfile_timeout = config.PIDFILE_TIMEOUT
           
    def run(self):
        while True:
            logger.info('Iniciando rotina de indexação...')
            lbindex.main()
            logger.info("""
                Indexação finalizada com sucesso!
                Pausa : %s
            """ % str(config.SLEEP_TIME))
            time.sleep(config.SLEEP_TIME)

logger = logging.getLogger("LBIndex")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(config.LOGFILE_PATH)
handler.setFormatter(formatter)
logger.addHandler(handler)
# Run Daemon
daemon_runner = runner.DaemonRunner(App())
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()
