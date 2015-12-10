#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import config
import logging
import datetime
import traceback
from multiprocessing import Pool

import requests
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError

from lbrest import LBRest
from liblightbase.lbutils.codecs import object2json


def index_registries(args):
    """Index each registry from base."""

    args_metadata = args["base"]["metadata"]
    base = args_metadata["name"]
    idx_exp_time = args_metadata["idx_exp_time"]
    txt_mapping = args_metadata.get("txt_mapping", None)

    args_index = args["index"]
    if args_index is not None:
        cfg_idx = args_index.get("cfg_idx", None)
    else:
        cfg_idx = None

    idx_exp_url = args_metadata["idx_exp_url"]

    while True:
        logger.info('STARTING PROCESS EXECUTION FOR %s' % base)
        try:
            base_indexer = BaseIndexer(
                base, idx_exp_time, 
                idx_exp_url, txt_mapping, cfg_idx)
            base_indexer.run_indexing()
        except (ConnectionError, Timeout) as e:
            logger.critical("""
                Could not connect to server! %s. 
                Waiting for %s minutes to run next.
                """ % (idx_exp_url, str(idx_exp_time))
            )
            time.sleep(datetime.timedelta(minutes=int(idx_exp_time)).seconds)

        except Exception as e:
            logger.critical('Uncaught Exception : %s' % traceback.format_exc())
            time.sleep(datetime.timedelta(minutes=int(idx_exp_time)).seconds)

class BaseIndexer():

    def __init__(self, base, idx_exp_time, idx_exp_url, txt_mapping, cfg_idx):
        self.base = base
        self.idx_exp_time = idx_exp_time

        # NOTE: "txt_mapping" é o mapeamento textual p/ a base em 
        # questão e "cfg_idx" é a configuração de indexação! By Questor
        self.lbrest = LBRest(
            base=base, idx_exp_url=idx_exp_url, 
            txt_mapping=txt_mapping, cfg_idx=cfg_idx)
        self.registries = self.lbrest.get_registries()

    def run_indexing(self):

        # NOTE: Check if Daemon has stopped!
        self.check_ppid()

        # NOTE: Get initial time!
        ti = datetime.datetime.now()

        for registry in self.registries:

            # NOTE: Check if Daemon has stopped!
            self.check_ppid()

            id = registry['_metadata']['id_doc']
            dt_last_up = registry['_metadata']['dt_last_up']

            # NOTE: Obtêm o registro com o texto extraído de arquivos 
            # anexos se houverem! By Questor
            full_reg = self.lbrest.get_full_reg(id, dt_last_up)

            # NOTE: For sequences (strings, lists, tuples), use the 
            # fact that empty sequences are false (PEP8)! By Questor
            if full_reg:
                indexed = self.lbrest.index_member(full_reg, id, dt_last_up)
                if indexed:
                    self.lbrest.update_dt_index(id, dt_last_up)

        self.delete_indices()

        # NOTE: Get final time!
        tf = datetime.datetime.now()
        self.sleep(ti, tf)

    # TODO: Existe uma rota "_index_error" que basicamente é 
    # consumida pelo método abaixo, entretanto só há leitura 
    # (GET) e deleção (DELETE) p/ ela. Não consegui localizar 
    # no LBGenerator nem no LBConverte uso pa essa rota, ou 
    # seja alguém que grave (POST) nela! Creio que seja o caso 
    # de remover os métodos abaixo e as suas ramificações! 
    # By Questor
    def delete_indices(self):
        """??????????????????????????????"""

        index_errors = self.lbrest.get_errors()
        for registry in index_errors:
            deleted = self.lbrest.delete_index(registry)
            if deleted:
                self.lbrest.delete_error(registry)

    def sleep(self, ti, tf):

        # NOTE: Calculate interval!
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

        # NOTE: Sleep interval!
        time.sleep(interval_seconds)

    def check_ppid(self):
        """Stop process if daemon is not running."""
        pid = os.getppid()
        if pid == 1:
            logger.info('STOPPING PROCESS EXECUTION FOR %s' % self.base)
            sys.exit(1)

logger = logging.getLogger("LBIndex")
