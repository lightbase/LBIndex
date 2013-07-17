#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests

from erros import *

import logging

logger = logging.getLogger("LBIndex")

def listarbases(domain):
    """Função que lista todas as bases"""
    
    values = {'$$':'{"select":["nome_base"]}'}
    url = domain + '/api/base'
    
    recebe = requests.get(url, params=values, timeout=15)
    json_resp = recebe.json()
    erro = is_error(json_resp)
    if erro:
        logger.critical('Erro ao conectar-se com as bases')
        logger.critical(str(json_resp['_status']) + ': ' +\
                        json_resp['_error_message'])
        bases = []
    else:
        bases = json_resp["results"]
    return bases