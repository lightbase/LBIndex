#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests

from erros import *

import logging

logger = logging.getLogger("LBIndex")

def listarregistros(domain, bases, force):
    """Função que lista todos os registros ainda não indexados"""
    
    listabases = []
    listaregs = []
    if force == 'sim':
        values = {'$$':'{"select":["id_reg"]}'}
    else:
        values = {'$$':'{"select":["id_reg"],"filters":[{"field":"dt_index_tex","term":null,"operation":"="}]}'}
    for x in bases:
        url = domain + '/api/reg/' + x['nome_base']

        recebe = requests.get(url, params=values, timeout=15)
        json_resp = recebe.json()
        erro = is_error(json_resp)
        if erro:
            logger.error('Erro ao conectar-se com a base \"' +\
                         x['nome_base'] + '\"')
            errorest(json_resp)
        else:
            listaregistros = json_resp["results"]
            for y in listaregistros:
                base = x['nome_base']
                reg = y['id_reg']
                listabases.append(base)
                listaregs.append(reg)
    return listabases, listaregs