#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser

import logging

logger = logging.getLogger("LBIndex")

def removebarra(url):
    if url[-1] == '/':
        url = url[0:-1]
    return url


def setconfiglbindex():
    """Função que recebe as configurações de modulo do usuario"""
    lbindex = {}
    config = ConfigParser.ConfigParser()
    config.read('development.ini')
    lbindex['domain'] = removebarra(config.get('LBIndex', 'domain'))
    elastic_search = removebarra(config.get('LBIndex', 'elastic_search'))
    elastic_door = config.get('LBIndex', 'elastic_door')
    lbindex['elastic'] = elastic_search + ':' + elastic_door + '/'
    lbindex['sleep_time'] = int(config.get('LBIndex', 'sleep_time'))
    lbindex['force_index'] = config.get('LBIndex', 'force_index')
    return lbindex


def setconfigdaemon():
    """Função que recebe as configurações de daemon do usuario"""
    daemon = {}
    config = ConfigParser.ConfigParser()
    config.read('development.ini')
    daemon['stdin_path'] = config.get('Daemon', 'stdin_path')
    daemon['stdout_path'] = config.get('Daemon', 'stdout_path')
    daemon['stderr_path'] = config.get('Daemon', 'stderr_path')
    pidfile_dir = removebarra(config.get('Daemon', 'pidfile_dir'))
    daemon['pidfile_path'] = pidfile_dir + '/lbindex.pid'
    daemon['logfile_dir'] = removebarra(config.get('Daemon', 'logfile_dir'))
    daemon['logfile_path'] = daemon['logfile_dir'] + '/lbindex.log'
    daemon['pidfile_timeout'] = int(config.get('Daemon', 'pidfile_timeout'))
    return daemon

# except ConfigParser.NoOptionError, x:
#     print "Erro no arquivo de configuração: " + str(x)