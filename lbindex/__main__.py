#!/usr/bin/python
# -*- coding: utf-8 -*-

# python lbindex start

from daemon import runner

from scripts import recebeconfig
from app import main

import logging
import time

class App():
   
    def __init__(self):
        self.stdin_path = daemon['stdin_path']
        self.stdout_path = daemon['stdout_path']
        self.stderr_path = daemon['stderr_path']
        self.pidfile_path = daemon['pidfile_path']
        self.pidfile_timeout = daemon['pidfile_timeout']
           
    def run(self):
        while True:
            logger.info('Iniciando rotina de indexação...')
            main(lbindex['domain'], lbindex['elastic'],
                 lbindex['force_index'])
            logger.info('Indexação finalizada com sucesso!')
            time.sleep(lbindex['sleep_time'])


daemon = recebeconfig.setconfigdaemon()
lbindex = recebeconfig.setconfiglbindex()
app = App()
logger = logging.getLogger("LBIndex")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(daemon['logfile_path'])
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

# python lbindex stop