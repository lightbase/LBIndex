# -*- coding: utf-8 -*-

import requests
import logging
import config
from pyelasticsearch import ElasticSearch
import datetime
import json

class LBRest():

    def __init__(self, base=None, index_url=None):
        self.base = base
        self.index_url = index_url

    def get_bases(self):
        """ Get all bases which has to index registries
        """
        bases = [ ]
        params = """{
            "select": [
                "nome_base",
                "index_time",
                "index_url"
            ],
            "literal": "index_export is true"
        }"""
        req = requests.get(config.REST_URL, params={'$$':params})
        try:
            req.raise_for_status()
            response = req.json()
            bases = response["results"]
        except:
            logger.error("""
                Erro ao tentar recuperar bases. url: %s. Reposta: %s
            """ % (config.REST_URL, req._content))
        return bases

    def get_passed_registries(self):
        registries = [ ]
        params = {'$$':"""{
            "select":["id_reg_orig", "dt_last_up_orig"],
            "literal": "base = '%s'",
            "limit": null
            }""" % self.base }
        url = config.REST_URL + '/log_lbindex/reg'
        req = requests.get(url, params=params)
        try:
            req.raise_for_status()
            response = req.json()
            registries = response["results"]
        except:
            logger.error("""
                Erro ao recuperar registros da base %s'. Resposta: %s
            """ % ('log_lbindex', req._content))

        return {reg['id_reg_orig']: reg['dt_last_up_orig'] for reg in registries}
        
    def get_registries(self):
        """Função que lista todos os registros a serem indexados"""
        registries = [ ]
        if config.FORCE_INDEX:
            params = {'$$':'{"select":["id_reg", "dt_last_up"]}'}
        else:
            params = {'$$':'{"select":["id_reg", "dt_last_up"],"literal":"dt_index_tex is null"}'}

        url = config.REST_URL + '/' + self.base + '/reg'
        req = requests.get(url, params=params)
        try:
            req.raise_for_status()
            response = req.json()
            registries = response["results"]
        except:
            logger.error("""
                Erro ao recuperar registros da base %s'. Resposta: %s
            """ % (self.base, req._content))

        passed = self.get_passed_registries()
        _registries = [ ]
        for reg in registries:
            if reg['id_reg'] in passed:
                dt_last_up = passed[reg['id_reg']]
                if dt_last_up != reg['dt_last_up']:
                    _registries.append(reg)
            else:
                _registries.append(reg)

        return _registries

    def get_full_reg(self, id, dt_last_up):
        logger.info('Recuperando registro %s da base %s ...' % (str(id), self.base))
        response = None
        url = config.REST_URL + '/' + self.base + '/reg/' + str(id) + '/full'
        req = requests.get(url)
        try:
            req.raise_for_status()
            response = req.json()
        except:
            error_msg = """
                Erro ao recuperar registro %s na base %s'. Resposta: %s
            """ % (str(id), self.base, req._content)
            logger.error(error_msg)
            write_error(id, dt_last_up, error_msg)
        return response

    def index_member(self, registry, id, dt_last_up):
        logger.info('Indexando registro %s da base %s na url %s ...' % (str(id), self.base, self.index_url))
        try:

            http, space, address, _index, _type = self.index_url.split('/')
            es = ElasticSearch('/'.join([http, space, address]))
            es.index(_index, _type, registry, id=id)
            return True

        except Exception as e:
            error_msg = """
                Erro ao indexar registro %s da base %s na url %s'. Mensagem de erro: %s
            """ % (str(id), self.base, self.index_url, str(e))
            logger.error(error_msg)
            self.write_error(id, dt_last_up, error_msg)
            return False

    def update_dt_index(self, id, dt_last_up):
        logger.info('Alterando data de indexacao do registro %s da base %s ...' % (str(id), self.base))
        params = {'dt_index_tex': str(datetime.datetime.now())}
        url = config.REST_URL + '/' + self.base + '/reg/' + str(id)
        req = requests.put(url, params=params)
        try:
            req.raise_for_status()
            return True
        except:
            error_msg = """
                Erro ao alterar data de indexacao do registro %s na base %s'. Resposta: %s
            """ % (str(id), self.base, req._content)
            logger.error(error_msg)
            self.write_error(id, dt_last_up, error_msg)
        return False

    def write_error(self, id_reg, dt_last_up, error_msg):
        """ Write errors to LightBase
        """
        error = {
            'base': self.base,
            'id_reg_orig': id_reg,
            'error_msg': error_msg,
            'dt_error': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'dt_last_up_orig': dt_last_up
        }
        url = config.REST_URL + '/log_lbindex/reg'
        data = {'json_reg': json.dumps(error)}
        req = requests.post(url, data=data)
        try:
            req.raise_for_status()
        except:
            logger.error("""
                Erro ao tentar escrever erro no Lightbase. Reposta: %s
            """ % req._content)

logger = logging.getLogger("LBIndex")

