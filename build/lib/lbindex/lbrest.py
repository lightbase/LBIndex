# -*- coding: utf-8 -*-
import json
import config
import logging
import requests
import datetime
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from pyelasticsearch.exceptions import IndexAlreadyExistsError
import model

logger = logging.getLogger("LBIndex")

class LBRest():

    def __init__(self, base=None, idx_exp_url=None):
        self.base = base
        self.idx_exp_url = idx_exp_url
        if self.idx_exp_url is not None:
            http, space, address, _index, _type = self.idx_exp_url.split('/')
            self.es = ElasticSearch('/'.join([http, space, address]))

    def get_bases(self):
        """ Get all bases which has to index registries
        """
        bases = [ ]
        params = """{
            "select": [
                "name",
                "idx_exp_time",
                "idx_exp_url"
            ],
            "literal": "idx_exp is true",
            "limit": null
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
        """
        Realiza leitura da base de log de indexação
        """
        # Cria base de log se não existir
        self.create_log_base()
        registries = [ ]
        params = {'$$':"""{
            "select":["id_doc_orig", "dt_last_up_orig"],
            "literal": "nm_base = '%s'",
            "limit": null
            }""" % self.base }
        url = config.REST_URL + '/log_lbindex/doc'
        req = requests.get(url, params=params)
        try:
            req.raise_for_status()
            response = req.json()
            registries = response["results"]
        except:
            logger.error("""
                Erro ao recuperar registros da base %s'. Resposta: %s
            """ % ('log_lbindex', req._content))


        resp = {} 
        for reg in registries:
            resp[reg['id_doc_orig']] = reg['dt_last_up_orig']
        return resp
        #return {reg['id_doc_orig']: reg['dt_last_up_orig'] for reg in registries}
        
    def get_registries(self):
        """Função que lista todos os registros a serem indexados"""
        registries = [ ]
        if config.FORCE_INDEX:
            params = {'$$':'{"select":["id_doc", "dt_last_up"], "limit": %d}'}
        else:
            params = {'$$':'{"select":["id_doc", "dt_last_up"],"literal":"dt_idx is null", "limit": %d}'}

        params.update(result_count='false')
        params['$$'] = params['$$'] % config.DEFAULT_LIMIT

        url = config.REST_URL + '/' + self.base + '/doc'
        req = requests.get(url, params=params)
        try:
            req.raise_for_status()
            response = req.json()
            registries = response["results"]
        except:
            logger.error("""
                Erro ao recuperar registros da base %s'. Resposta: %s
            """ % (self.base, req._content))





        # Erro ao recuperar registros da base docs_pro'. Resposta: {"status": 500, 
        # "request": {"path": "/api/docs_pro/doc", "client_addr": "10.72.246.21", 
        #         "user_agent": "python-requests/2.3.0 CPython/2.6.6 Linux/2.6.32-504.el6.x86_64", 
        #         "method": "GET"}, "error_message": "SearchError: (OperationalError) could not 
        # connect to server: No route to host\n\tIs the server running on host \"10.72.247.144\" 
        # and accepting\n\tTCP/IP connections on port 5432?\n None None", "type": "Exception"}





        passed = self.get_passed_registries()
        _registries = [ ]
        for reg in registries:
            if reg['_metadata']['id_doc'] in passed:
                dt_last_up = passed[reg['_metadata']['id_doc']]
                if dt_last_up != reg['_metadata']['dt_last_up']:
                    _registries.append(reg)
            else:
                _registries.append(reg)

        return _registries

    def get_full_reg(self, id, dt_last_up):
        logger.info('Recuperando registro %s da base %s ...' % (str(id), self.base))
        response = None
        url = config.REST_URL + '/' + self.base + '/doc/' + str(id) + '/full'
        req = requests.get(url)
        try:
            req.raise_for_status()
            response = req.json()
        except:
            error_msg = """
                Erro ao recuperar registro %s na base %s'. Resposta: %s
            """ % (str(id), self.base, req._content)
            logger.error(error_msg)
            self.write_error(id, dt_last_up, error_msg)
        return response

    def index_member(self, registry, id, dt_last_up):
        logger.info('Indexando registro %s da base %s na url %s ...' % (str(id), self.base, self.idx_exp_url))
        try:

            http, space, address, _index, _type = self.idx_exp_url.split('/')
            self.es.index(_index, _type, registry, id=id)
            return True

        except Exception as e:
            error_msg = """
                Erro ao indexar registro %s da base %s na url %s'. Mensagem de erro: %s
            """ % (str(id), self.base, self.idx_exp_url, str(e))
            logger.error(error_msg)
            self.write_error(id, dt_last_up, error_msg)
            return False

    def update_dt_index(self, id, dt_last_up):
        logger.info('Alterando data de indexacao do registro %s da base %s ...' % (str(id), self.base))
        params = {'value': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        url = config.REST_URL + '/' + self.base + '/doc/' + str(id) + '/_metadata/dt_idx'
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

    def write_error(self, id_doc, dt_last_up, error_msg):
        """ Write errors to LightBase
        """
        error = {
            'nm_base': self.base,
            'id_doc_orig': id_doc,
            'error_msg': error_msg,
            'dt_error': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'dt_last_up_orig': dt_last_up
        }
        url = config.REST_URL + '/log_lbindex/doc'
        data = {'value': json.dumps(error)}
        req = requests.post(url, data=data)
        try:
            req.raise_for_status()
        except:
            logger.error("""
                Erro ao tentar escrever erro no Lightbase. Reposta: %s
            """ % req._content)

    def get_errors(self):
        """ Get all bases which has to index registries
        """
        errors = [ ]
        params = """{
            "literal": "base = '%s'",
            "limit": 250
        }""" % (self.base)
        url = config.REST_URL + '/_index_error'
        req = requests.get(url, params={'$$':params})
        try:
            req.raise_for_status()
            response = req.json()
            errors = response["results"]
        except:
            logger.error("""
                Erro ao tentar recuperar erros de indice. url: %s. Reposta: %s
            """ % (url, req._content))
        return errors

    def create_index(self):
        """
        Cria índice com as opções de mapeamento padrão
        Atualiza o índice se já estiver criado
        """
        settings = {
            "settings": {
                # "number_of_shards": "5",
                # "number_of_replicas": "1",
                "analysis.analyzer.default.filter.0": "lowercase",
                "analysis.analyzer.default.filter.1": "asciifolding",
                "analysis.analyzer.default.tokenizer": "standard",
                "analysis.analyzer.default.type": "custom",
                "analysis.filter.pt_stemmer.type": "stemmer",
                "analysis.filter.pt_stemmer.name": "portuguese"
            },
            "mappings": {
                "document": {
                    "_timestamp": {
                        "enabled": "true"
                    }
                }
            }
        }

        http, space, address, _index, _type = self.idx_exp_url.split('/')
        try:
            result = self.es.create_index(
                index=_index,
                settings=settings
            )
        except IndexAlreadyExistsError as e:
            logger.info("O índice já existe. Tentando atualizar o mapping...")
            self.es.close_index(index=_index)
            result = self.es.update_settings(
                index=_index,
                settings=settings
            )
            logger.info("Mapping atualizado com sucesso. Abrindo o índice...")
            self.es.open_index(index=_index)
            logger.info("Índice reaberto com sucesso!")

    def delete_index(self, registry):
        id = registry['id_doc']
        try:
            http, space, address, _index, _type = self.idx_exp_url.split('/')
            self.es.delete(_index, _type, id=id)
            return True

        except ElasticHttpNotFoundError as e:
            return True

        except Exception as e:
            error_msg = """
                Erro ao deletar indice %s da base %s na url %s'. Mensagem de erro: %s
            """ % (str(id), self.base, self.idx_exp_url, str(e))
            logger.error(error_msg)
            return False

    def delete_error(self, registry):
        url = config.REST_URL + """/_index_error?$$={"literal":"base = '%s' and id_doc = %d"}"""
        url = url % (registry['base'], registry['id_doc'])
        logger.info('Deletando registro de erro de indice na url %s' % url)
        req = requests.delete(url)
        try:
            req.raise_for_status()
            return True
        except:
            error_msg = """
                Erro ao deletar erro de indice. Resposta: %s
            """ % (req._content)
            logger.error(error_msg)
        return False

    @staticmethod
    def create_log_base():
        """
        Cria base de log do índice caso não exista
        """
        log_base = model.LogBase()
        response = log_base.get_base()
        if not response:
            # Cria a base já que ela não existe
            logger.info("Criando base de log do índice...")
            result = log_base.create_base()
            if result is None:
                logger.error("Erro na criação da base de log: \n%s", response.text)
                return False
            else:
                logger.info("Base de log criada com sucesso!")

        return True
