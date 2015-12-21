# -*- coding: utf-8 -*-

import ConfigParser

def set_config():

    config = ConfigParser.ConfigParser()
    config.read('production.ini')
    #config.read('development.ini')

    global REST_URL
    global FORCE_INDEX
    global PIDFILE_PATH
    global LOGFILE_PATH
    global DEFAULT_LIMIT
    global BASE_FORCE
    global ES_URL
    global NM_BASE
    global TIME_IDX

    #---------------------#
    # Configuration Start #
    #---------------------#

    # LBIndex configuration 
    REST_URL = config.get('LBIndex', 'rest_url')
    FORCE_INDEX = config.get('LBIndex', 'force_index')
    if FORCE_INDEX == 'true':
        FORCE_INDEX = True
    elif FORCE_INDEX == 'false':
        FORCE_INDEX = False
    else:
        raise Exception('opcao "force_index" deve ser "true" ou "false"!')

    DEFAULT_LIMIT = int(config.get('LBIndex', 'default_limit'))

    # Daemon configuration 
    PIDFILE_PATH = config.get('Daemon', 'pidfile_path')
    LOGFILE_PATH = config.get('Daemon', 'logfile_path')

    ES_URL = config.get('LBIndex', 'es_url')
    NM_BASE = config.get('LBIndex', 'nm_base')
    TIME_IDX = config.get('LBIndex', 'time_idx')

    #-------------------#
    # Configuration End #
    #-------------------#
