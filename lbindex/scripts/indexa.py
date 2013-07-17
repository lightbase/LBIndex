#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyelasticsearch import ElasticSearch
import requests

from erros import *

from datetime import datetime
import logging

logger = logging.getLogger("LBIndex")

def indexar(domain, elastic, listabases, listaregs):
    """
    Função que lança os registros no elasticsearch e
    marca na base a data e hora da indexação
    """
    
    es = ElasticSearch(elastic)
    for reg, base in zip(listaregs, listabases):
        urles = elastic + base + '/' + base + '/' + str(reg)
        urlrest = domain + '/api/reg/' + base + '/' + str(reg)
        urlfull = urlrest + '/full'
        
        recebe = requests.get(urlfull, timeout=15)
        json_resp = recebe.json()
        erro = is_error(json_resp)
        if erro:
            logger.error('Erro ao conectar-se com o registro \"' +\
                         str(reg) + '\" da base \"' + base + '\"')
            errorest(json_resp)
        else:
            es.index(base,base, json_resp, id=reg)
            logger.info(urles + ' indexado com sucesso!')
               
            values = {'$method': 'PUT', 'dt_index_tex': str(datetime.now())}
            json_resp2 = requests.put(urlrest, data=values)
            erro2 = is_error(json_resp2)
            if erro2:
                logger.error('Erro ao incluir data/hora no registro \"' +\
                             str(reg) + '\" da base \"' + base + '\"')
                errorest(json_resp2)