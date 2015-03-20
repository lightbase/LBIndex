# -*- coding: utf-8 -*-

import os
import sys
import time
import config
import logging
import datetime
import traceback
from lbrest import LBRest
from multiprocessing import Pool
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError

def index_registries(args):
    """ Index each registry from base """

    base = args['metadata']['name']
    idx_exp_time = args['metadata']['idx_exp_time']
    idx_exp_url = args['metadata']['idx_exp_url']

    while True:
        #logger.info('STARTING PROCESS EXECUTION FOR %s' % base)

        try:
            base_indexer = BaseIndexer(base, idx_exp_time, idx_exp_url)
            base_indexer.run_indexing()

        except (ConnectionError, Timeout) as e:
            logger.critical('Could not connect to server! ' + idx_exp_url)

        except Exception as e:
            logger.critical('Uncaught Exception : %s' % traceback.format_exc())

class BaseIndexer():

    def __init__(self, base, idx_exp_time, idx_exp_url):
        self.base = base
        self.idx_exp_time = idx_exp_time
        self.lbrest = LBRest(base, idx_exp_url)
        self.registries = self.lbrest.get_registries()

    def run_indexing(self):

        # Check if Daemon has stopped
        self.check_ppid()

        # Get initial time
        ti = datetime.datetime.now()

        for registry in self.registries:

            # Check if Daemon has stopped
            self.check_ppid()

            id = registry['_metadata']['id_doc']
            dt_last_up = registry['_metadata']['dt_last_up']

            full_reg = self.lbrest.get_full_reg(id, dt_last_up)

            if full_reg:
                indexed = self.lbrest.index_member(full_reg, id, dt_last_up)

                if indexed:
                    self.lbrest.update_dt_index(id, dt_last_up)

        self.delete_indices()

        # Get final time
        tf = datetime.datetime.now()
        self.sleep(ti, tf)

    def delete_indices(self):
        index_errors = self.lbrest.get_errors()

        for registry in index_errors:

            deleted = self.lbrest.delete_index(registry)

            if deleted:
                self.lbrest.delete_error(registry)

    def sleep(self, ti, tf):

        # Calculate interval
        execution_time = tf - ti
        _idx_exp_time = datetime.timedelta(minutes=self.idx_exp_time)

        if execution_time >= _idx_exp_time:
            interval = 0
        else:
            interval = _idx_exp_time - execution_time

        if type(interval) is not int:
            interval_minutes = (interval.seconds//60)%60
            interval_seconds = interval.seconds
        else:
            interval_minutes = interval_seconds = interval

        #logger.info('Finished execution for base %s, will wait for %s minutes'
        #    % (self.base, str(interval_minutes)))

        # Sleep interval
        time.sleep(interval_seconds)

    def check_ppid(self):
        """ Stop process if daemon is not running
        """
        pid = os.getppid()
        if pid == 1:
            logger.info('STOPPING PROCESS EXECUTION FOR %s' % self.base)
            sys.exit(1)

logger = logging.getLogger("LBIndex")
