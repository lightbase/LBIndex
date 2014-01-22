# -*- coding: utf-8 -*-

import logging
from lbrest import LBRest
from multiprocessing import Pool
import config
import datetime
import time
import os
import sys

def main():
    """
    """
    lbrest = LBRest()
    bases = lbrest.get_bases()
    if bases:
        pool = Pool(processes=len(bases))
        pool.map(index_registries, bases)

def index_registries(args):
    """ Index each registry from base """

    base = args['nome_base']
    index_time = args['index_time']
    index_url = args['index_url']

    while(1):
        logger.info('STARTING PROCESS EXECUTION FOR %s' % base)
        # Get initial time
        ti = datetime.datetime.now()

        # Execute process
        base_indexer = BaseIndexer(base, index_url)
        base_indexer.run_indexing()

        # Get final time
        tf = datetime.datetime.now()

        # Calculate interval
        execution_time = tf - ti
        _index_time = datetime.timedelta(minutes=index_time)

        if execution_time >= _index_time:
            interval = 0
        else:
            interval = _index_time - execution_time

        interval_minutes = (interval.seconds//60)%60

        #logger.info('Finished execution for base %s, will wait for %s minutes' % (base, interval_minutes))
        logger.info('Finished execution for base %s, will wait for %s seconds' % (base, interval.seconds))

        # Sleep interval
        time.sleep(interval.seconds)
        pid = os.getppid()
        if pid == 1:
            logger.info('STOPPING PROCESS EXECUTION FOR %s' % base)
            sys.exit(1)

class BaseIndexer():

    def __init__(self, base, index_url):
        self.base = base
        self.lbrest = LBRest(base, index_url)
        self.registries = self.lbrest.get_registries()

    def run_indexing(self):

        for registry in self.registries:
            id = registry['id_reg']
            full_reg = self.lbrest.get_full_reg(id)

            if full_reg:
                indexed = self.lbrest.index_member(full_reg, id)

                if indexed:
                    self.lbrest.update_dt_index(id)

logger = logging.getLogger("LBIndex")
