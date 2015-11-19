#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import config
import logging
import datetime

import requests

from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from pyelasticsearch.exceptions import IndexAlreadyExistsError
import model

logger = logging.getLogger("LBIndex")


class LBRest():

    def __init__(self, base=None, idx_exp_url=None, 
                 txt_mapping=None, cfg_idx=None):
        """Serve para cosumir o LBG e o ES."""

        self.base = base
        self.idx_exp_url = idx_exp_url
        if self.idx_exp_url is not None:
            self.idx_exp_host = idx_exp_url.split('/')[2]
            self.idx_exp_index = idx_exp_url.split('/')[3]
            self.idx_exp_type = idx_exp_url.split('/')[4]
            self.es = ElasticSearch("http://" + self.idx_exp_host)
        self.txt_mapping = txt_mapping
        self.cfg_idx = cfg_idx
        self.con_refsd = False

    def get_index(self, bases_list):
        """Obter a a configuração de indexação p/ as bases."""

        bases_indexes = []
        for base in bases_list:
            idx_exp_url = base['metadata']['idx_exp_url']
            nm_idx = idx_exp_url.split('/')[3]
            url_txt_idx = config.REST_URL + "/_txt_idx/" + nm_idx
            req = None
            try:
                req = requests.get(url_txt_idx)
                req.raise_for_status()
                idx_resp = req.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:

                    # NOTE: Para os casos onde não há configuração de 
                    # indexação setada na rota "_txt_idx"! By Questor
                    idx_resp = None
                else:
                    fail_content = None
                    if req is not None:
                        fail_content = req._content
                    else:
                        fail_content = str(e)
                    logger.error("Falha HTTP ao tentar obter configuração de "\
                    "índice textual! URL: %s. FALHA: %s" % 
                    (config.REST_URL, fail_content))
                    return []
            except Exception as e:
                fail_content = None
                if req is not None:
                    fail_content = req._content
                else:
                    fail_content = str(e)
                logger.error("Erro ao tentar obter a configuração de índice "\
                "textual! URL: %s. FALHA: %s" % 
                (config.REST_URL, fail_content))
                return []
            bases_indexes.append({"base": base, "index": idx_resp})
        return bases_indexes

    def get_bases(self):
        """Get all bases which has to index registries."""

        # NOTE: A construção logo abaixo tá meio tosca. O objetivo é
        # checar se na estrutura de dados da table "lb_base" já está 
        # o atributo (campo struct) e o campo "txt_mapping". Se não 
        # tiver, tenta obter a base com todos os campos. Trata-se de 
        # um "workaround" sendo o correto que a estrutura de dados 
        # na table "lb_base" esteja atualizada! By Questor
        bases = [ ]
        req = None
        try:
            params = """{
                "select": [
                    "name",
                    "idx_exp_time",
                    "idx_exp_url",
                    "txt_mapping"
                ],
                "literal": "idx_exp is true",
                "limit": null
            }"""
            req = requests.get(config.REST_URL, params={'$$':params})
            req.raise_for_status()
            response = req.json()
            bases = response["results"]
        except Exception as e:
            bases = [ ]
            req = None
            try:
                params = """{
                    "literal": "idx_exp is true",
                    "limit": null
                }"""
                req = requests.get(config.REST_URL, params={'$$':params})
                req.raise_for_status()
                response = req.json()
                bases = response["results"]
            except Exception as e:
                # NOTE: A variável de instância "self.con_refsd" 
                # serve p/ evitar que o aviso mais abaixo seja 
                # exibido repetidamente detonando o log! By Questor
                if self.con_refsd:
                    return bases

                # NOTE: Estou usando '"Connection refused" in str(e)' 
                # pq "raise_for_status()" mais acima não retorna uma 
                # exceção do tipo "requests.exceptions.HTTPError" de 
                # forma q possamos usar o código em "status_code" 
                # tratar erro de forma mais específica! By Questor
                if "Connection refused" in str(e) and not self.con_refsd:
                    logger.error('Erro ao obter a lista bases para '\
                    'indexação. URL: %s. FALHA: Servidor indisponivel! '\
                    'HTTPCode: 502 (Connection refused)!' % (config.REST_URL))
                    self.con_refsd = True
                    return bases
                self.con_refsd = False
                fail_content = None
                if req is not None:
                    fail_content = req._content
                else:
                    fail_content = str(e)
                logger.error("""
                    Erro ao obter a lista bases para indexação. URL: %s. FALHA: %s
                """ % (config.REST_URL, fail_content))
        return bases

    def get_passed_registries(self):
        """Retorna registros da base de log erros de indexação. 
        Apenas "id_doc_orig" e "dt_last_up_orig".
        """

        # NOTE: Cria base de log se não existir! By Questor
        self.create_log_base()

        registries = [ ]
        params = {'$$':"""{
            "select":["id_doc_orig", "dt_last_up_orig"],
            "literal": "nm_base = '%s'",
            "limit": null
            }""" % self.base}
        url = config.REST_URL + '/log_lbindex/doc'

        req = None
        try:
            req = requests.get(url, params=params)
            req.raise_for_status()
            response = req.json()
            registries = response["results"]
        except Exception as e:
            fail_content = None
            if req is not None:
                fail_content = req._content
            else:
                fail_content = str(e)
            logger.error("""
                1 Erro ao recuperar registros da base %s'. FALHA: %s
            """ % ('log_lbindex', fail_content))

        resp = {}
        for reg in registries:
            resp[reg['id_doc_orig']] = reg['dt_last_up_orig']
        return resp

    def get_registries(self):
        """Retorna registros à serem indexados que sob certos critérios não 
        tenham falhado no passado.
        """

        # NOTE: Obtêm registros da base de log de erros! Registros 
        # q tenham falhado no passado! By Questor
        registries = [ ]
        if config.FORCE_INDEX:
            params = {'$$':'{"select":["id_doc", "dt_last_up"], "limit": %d}'}
        else:
            params = {
                '$$':'{"select":["id_doc", "dt_last_up"], \
                "literal":"dt_idx is null", "limit": %d}'
            }

        params.update(result_count='false')
        params['$$'] = params['$$'] % config.DEFAULT_LIMIT

        url = config.REST_URL + '/' + self.base + '/doc'

        req = None
        try:
            req = requests.get(url, params=params)
            req.raise_for_status()
            response = req.json()
            registries = response["results"]
        except Exception as e:
            fail_content = None
            if req is not None:
                fail_content = req._content
            else:
                fail_content = str(e)
            logger.error("""
                Erro ao recuperar registros da base %s'. FALHA: %s
            """ % (self.base, fail_content))

        '''
        TODO: Essa lógica poderia ser mais eficiente... A 
        princípio vejo duas soluções...
        1 - Guardar em cache (mais complicada);
        2 - Trazer apenas os registros (id_doc) envolvidos 
        no processo de indexação atual.
        By Questor
        '''

        '''
        TODO: Esse método "self.get_passed_registries()" deveria 
        ser chamado sempre? Mesmo quando a operação é "create"? 
        Checar melhor... By Questor
        '''

        # NOTE: Obtêm registros da base de log de erros! Registros 
        # q tenham falhado no passado! By Questor
        passed = self.get_passed_registries()

        _registries = [ ]
        for reg in registries:
            if reg['_metadata']['id_doc'] in passed:
                '''
                NOTE: O objetivo aqui é checar se o registro 
                está no log de erros (registros que tentou-se 
                indexar no passado) e se estiver ignora-os a 
                não ser que a data de "update" do registro 
                registrado na base de logs seja diferente da 
                data atual do registro, nesses casos o LBIndex 
                vai tentar novamente!
                By Questor
                '''

                '''
                NOTE: No dict "passed" consta apenas o valor 
                do campo "dt_last_up_orig" da base "log_lbindex"! 
                By Questor
                '''
                dt_last_up = passed[reg['_metadata']['id_doc']]

                if dt_last_up != reg['_metadata']['dt_last_up']:
                    _registries.append(reg)
            else:
                _registries.append(reg)

        return _registries

    def get_full_reg(self, id, dt_last_up):
        """Obtêm o registro doc mais textos extraídos dos arquivos anexos se 
        houverem.
        """

        # TODO: Registrar essa ação no log toda "santa vez"? By Questor
        logger.info('Recuperando registro %s da base %s ...' % 
            (str(id), self.base))

        response = None
        url = config.REST_URL + '/' + self.base + '/doc/' + str(id) + '/full'

        req = None
        try:
            req = requests.get(url)
            req.raise_for_status()
            response = req.json()
        except Exception as e:
            fail_content = None
            if req is not None:
                fail_content = req._content
            else:
                fail_content = str(e)
            error_msg = """
                Erro ao recuperar registro %s na base %s'. FALHA: %s
            """ % (str(id), self.base, fail_content)

            # TODO: Pq duas chamadas as logs? By Questor
            logger.error(error_msg)
            self.write_error(id, dt_last_up, error_msg)
        return response

    def es_create_mapping(self):
        """Cria um mapping p/ uma base se houver configuração p/ isso."""

        response_0 = None
        response_0_json = None
        index_url = None
        try:
            index_url = ("http://" + self.idx_exp_host + "/" + 
                self.idx_exp_index + "/" + self.idx_exp_type)
            response_0 = requests.get(index_url + "/_mapping")
            response_0.raise_for_status()
            response_0_json = response_0.json()
        except requests.exceptions.HTTPError as e:

            # NOTE: Normalmente entrará nesse bloco de código 
            # quando o índice não existe! By Questor
            self.es_create_index()
        except requests.exceptions.RequestException as e:
            raise Exception("Problem in the mapping provider! " + str(e))
        except Exception as e:
            raise Exception("Mapping operation. Program error! " + str(e))

        if (response_0.status_code == 200 and not response_0_json and 
                (self.txt_mapping is not None and self.txt_mapping)):
            response_1 = None
            try:
                response_1 = self.es.put_mapping(
                    index=self.idx_exp_index,
                    doc_type=self.idx_exp_type,
                    mapping=self.txt_mapping)

                if (response_1 is None or
                        response_1.get("acknowledged", None) is None or
                        response_1.get("acknowledged", None) != True):
                    raise Exception("Retorno inesperado do servidor \
                        ao criar mapping! " + 
                        str(response_1))
            except Exception as e:
                raise Exception("Mapping creation error! " + str(e))

    def es_create_index(self):
        """Criar um índice p/ a base com as configurações setadas, não havendo 
        criar um índice genérico.
        """

        response_0 = None
        try:
            cfg_idx_holder = None

            # NOTE: Se não houver configuração de indexação "setada" 
            # o sistema vai criar uma padrão! By Questor
            if self.cfg_idx is not None and self.cfg_idx:
                cfg_idx_holder = self.cfg_idx
            else:
                cfg_idx_holder = {
                        "settings":{
                            "analysis":{
                                "analyzer":{
                                    "default":{
                                        "tokenizer":"standard",
                                        "filter":[
                                            "lowercase",
                                            "asciifolding"
                                        ]
                                    }
                                }
                            }
                        }
                    }

            response_0 = self.es.create_index(index=self.idx_exp_index,
                                              settings=cfg_idx_holder)

            if (response_0 is None or
                response_0.get("acknowledged", None) is None or
                response_0.get("acknowledged", None) != True):
                raise Exception("Retorno inesperado do servidor \
                    ao criar index! " + 
                    str(response_0))

            self.es_create_mapping()
        except IndexAlreadyExistsError as e:
            self.es_create_mapping()
        except Exception as e:
            raise Exception("Index creation error! " + str(e))

    def index_member(self, registry, id, dt_last_up):
        """Criar o índice textual para cada registro."""

        logger.info('Indexando registro %s da base %s na url %s ...' % (str(id), self.base, self.idx_exp_url))

        try:

            # NOTE: Trata e cria os mappings e index textuais! 
            # By Questor
            self.es_create_mapping()
            self.es.index(self.idx_exp_index, self.idx_exp_type, 
                          registry, id=id)
            return True
        except Exception as e:
            error_msg = """
                Erro ao indexar registro %s da base %s na url %s'. Mensagem de erro: %s
            """ % (str(id), self.base, self.idx_exp_url, str(e))
            logger.error(error_msg)

            # TODO: Pq dois logs? By Questor
            self.write_error(id, dt_last_up, error_msg)
            return False

    def update_dt_index(self, id, dt_last_up):
        """Atualizar a data de atualização da indexação textual do registro."""

        logger.info('Alterando data de indexacao do '\
            'registro %s da base %s ...' % (str(id), self.base))
        params = {'value': datetime.datetime.now().\
            strftime('%d/%m/%Y %H:%M:%S')}
        url = (config.REST_URL + '/' + self.base + '/doc/' + str(id) + 
            '/_metadata/dt_idx')

        req = None
        try:
            req = requests.put(url, params=params)
            req.raise_for_status()
            return True
        except Exception as e:
            fail_content = None
            if req is not None:
                fail_content = req._content
            else:
                fail_content = str(e)
            error_msg = 'Erro ao alterar data de indexacao do registro %s na '\
                'base %s. FALHA: %s' % (str(id), self.base, fail_content)
            logger.error(error_msg)
            self.write_error(id, dt_last_up, error_msg)
        return False

    def write_error(self, id_doc, dt_last_up, error_msg):
        """Write errors to LightBase."""

        error = {
            'nm_base': self.base,
            'id_doc_orig': id_doc,
            'error_msg': error_msg,
            'dt_error': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'dt_last_up_orig': dt_last_up
        }
        url = config.REST_URL + '/log_lbindex/doc'
        data = {'value': json.dumps(error)}
        req = None
        try:
            req = requests.post(url, data=data)
            req.raise_for_status()
        except Exception as e:
            fail_content = None
            if req is not None:
                fail_content = req._content
            else:
                fail_content = str(e)
            logger.error("""
                0 Erro ao tentar escrever erro no Lightbase. FALHA: %s
            """ % fail_content)

    def get_errors(self):
        """Get all bases which has to index registries."""

        errors = [ ]
        params = """{
            "literal": "base = '%s'",
            "limit": 250
        }""" % (self.base)
        url = config.REST_URL + '/_index_error'

        req = None
        try:
            req = requests.get(url, params={'$$':params})
            req.raise_for_status()
            response = req.json()
            errors = response["results"]
        except Exception as e:
            fail_content = None
            if req is not None:
                fail_content = req._content
            else:
                fail_content = str(e)
            logger.error("""
                Erro ao tentar recuperar erros de indice. URL: %s. FALHA: %s
            """ % (url, fail_content))
        return errors

    # TODO: Esse método serve para criar/atualizar p/ uma 
    # indexação (index) padrão! No momento está "desvirtuado", 
    # pois basta apagar o índice p/ q ele seja recriado com a 
    # indexação setada na rota "_txt_idx"! Creio que esse 
    # método não faz muito sentido aqui. Sugiro remover! 
    # By Questor
    def create_index(self):
        """Cria índice com as opções de mapeamento padrão
        Atualiza o índice se já estiver criado.
        """

        settings = {
            "settings":{
                "analysis":{
                    "analyzer":{
                        "default":{
                            "tokenizer":"standard",
                            "filter":[
                                "lowercase",
                                "asciifolding"
                            ]
                        }
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
        """Deletar registros no index."""

        id = registry['id_doc']
        try:
            http, space, address, _index, _type = self.idx_exp_url.split('/')
            self.es.delete(_index, _type, id=id)
            return True

        except ElasticHttpNotFoundError as e:
            return True

        except Exception as e:
            error_msg = 'Erro ao deletar indice %s da base %s na url %s. '\
                'Mensagem de erro: %s' % \
                (str(id), self.base, self.idx_exp_url, str(e))
            logger.error(error_msg)
            return False

    def delete_error(self, registry):
        """Deletar registro de erros na rota '_index_error'."""

        url = (config.REST_URL + 
            """/_index_error?$$={"literal":"base = '%s' and id_doc = %d"}""")
        url = url % (registry['base'], registry['id_doc'])
        logger.info('Deletando registro de erro de indice na url %s' % url)

        req = None
        try:
            req = requests.delete(url)
            req.raise_for_status()
            return True
        except Exception as e:
            fail_content = None
            if req is not None:
                fail_content = req._content
            else:
                fail_content = str(e)
            error_msg = """
                Erro ao deletar erro de indice. FALHA: %s
            """ % (fail_content)
            logger.error(error_msg)
        return False

    @staticmethod
    def create_log_base():
        """Cria base de log do LBIndex caso não exista."""

        log_base = model.LogBase()
        response = log_base.get_base()
        if not response:

            # NOTE: Cria a base já que ela não existe!
            logger.info("Criando base de log do índice...")
            result = log_base.create_base()
            if result is None:
                logger.error("Erro na criação da base de log: \n%s", 
                             response.text)
                return False
            else:
                logger.info("Base de log criada com sucesso!")
        return True
