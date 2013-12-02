

def set_config():

    import ConfigParser

    config = ConfigParser.ConfigParser()
    #config.read('production.ini')
    config.read('development.ini')

    global REST_URL
    global ELASTIC_SEARCH_URL
    global FORCE_INDEX
    global SLEEP_TIME
    global STDIN_PATH
    global STDOUT_PATH
    global STDERR_PATH
    global PIDFILE_PATH
    global LOGFILE_PATH
    global PIDFILE_TIMEOUT

    #---------------------#
    # Configuration Start #
    #---------------------#

    # LBIndex configuration 
    REST_URL = config.get('LBIndex', 'rest_url')
    ELASTIC_SEARCH_URL = config.get('LBIndex', 'elastic_search_url')
    FORCE_INDEX = config.get('LBIndex', 'force_index')
    if FORCE_INDEX == 'true':
        FORCE_INDEX = True
    elif FORCE_INDEX == 'false':
        FORCE_INDEX = False
    else:
        raise Exception('opcao "force_index" deve ser "true" ou "false"!')
    SLEEP_TIME = int(config.get('LBIndex', 'sleep_time'))

    # Daemon configuration 
    STDIN_PATH = config.get('Daemon', 'stdin_path')
    STDOUT_PATH = config.get('Daemon', 'stdout_path')
    STDERR_PATH = config.get('Daemon', 'stderr_path')
    PIDFILE_PATH = config.get('Daemon', 'pidfile_path')
    LOGFILE_PATH = config.get('Daemon', 'logfile_path')
    PIDFILE_TIMEOUT = int(config.get('Daemon', 'pidfile_timeout'))

    #-------------------#
    # Configuration End #
    #-------------------#

