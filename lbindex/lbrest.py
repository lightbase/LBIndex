# -*- coding: utf-8 -*-

import requests
import logging
import config
from lbparse import RegistryParser
from pyelasticsearch import ElasticSearch
from datetime import datetime

def get_bases():
    """Função que lista todas as bases"""
    bases = None
    logger.info('Recuperando bases ...')
    params = """{
        "select": [
            "id_base",
            "nome_base",
            "index_time",
            "index_url"
        ],
        "literal": "index_export is true"
    }"""
    params = {'$$':'{"select":["nome_base"]}'}
    req = requests.get(config.REST_URL, params=params)
    try:
        req.raise_for_status()
        response = req.json()
        bases = response["results"]
    except:
        logger.error("""
            Erro ao tentar recuperar bases. url: %s. Reposta: %s
        """ % (config.REST_URL, req._content))
    return bases

def get_base_json(id):
    """Get base json"""
    base_json = None
    logger.info('Recuperando json da base id= ...' % str(id))
    url = config.REST_URL + '/' + str(id)
    req = requests.get(url)
    try:
        req.raise_for_status()
        response = req.json()
        base_json = response["json_base"]
    except:
        logger.error("""
            Erro ao tentar recuperar json da base id=%s.  url: %s. Reposta: %s
        """ % (str(id), url, req._content))
    return base_json

def get_registries(base):
    """Função que lista todos os registros a serem indexados"""
    registries = None
    logger.info('Recuperando registros da base %s ...' % base)
    if config.FORCE_INDEX:
        params = {'$$':'{"select":["id_reg"]}'}
    else:
        params = {'$$':'{"select":["id_reg"],"literal":"dt_index_tex is null"}'}

    url = config.REST_URL + '/' + base + '/reg'
    req = requests.get(url, params=params)
    try:
        req.raise_for_status()
        response = req.json()
        registries = response["results"]
    except:
        logger.error("""
            Erro ao recuperar registros da base %s'. Resposta: %s
        """ % (base, req._content))
    return registries

def get_full_reg(base, id):
    logger.info('Recuperando registro %s da base %s ...' % (str(id), base))
    response = None
    url = config.REST_URL + '/' + base + '/reg/' + str(id) + '/full'
    req = requests.get(url)
    try:
        req.raise_for_status()
        response = req.json()
    except:
        logger.error("""
            Erro ao recuperar registro %s na base %s'. Resposta: %s
        """ % (str(id), base, req._content))

    return response


def index_member(base, base_json, registry, id):
    logger.info('Analisando registro %s da base %s ...' % (str(id), base))
    try:
        parser = RegistryParser(base_json, registry)
        registry = parser.parse()
    except Exception as e:
        logger.error("""
            Erro ao analisar registro %s na base %s'. Mensagem de erro: %s
        """ % (str(id), base, str(e)))
    logger.info('Indexando registro %s da base %s ...' % (str(id), base))
    try:
        es = ElasticSearch(config.ELASTIC_SEARCH_URL)
        es.index(base, base, registry, id=id)
        return True
    except Exception as e:
        logger.error("""
            Erro ao indexar registro %s na base %s'. Mensagem de erro: %s
        """ % (str(id), base, str(e)))
        return False

def update_dt_index(base, id):
    response = None
    logger.info('Alterando data de indexacao do registro %s da base %s ...' % (str(id), base))
    params = {'dt_index_tex': str(datetime.now())}
    url = config.REST_URL + '/' + base + '/reg/' + str(id)
    req = requests.put(url, params=params)
    try:
        req.raise_for_status()
        return True
    except:
        logger.error("""
            Erro ao alterar data de indexacao do registro %s na base %s'. Resposta: %s
        """ % (str(id), base, req._content))
    return response

logger = logging.getLogger("LBIndex")
