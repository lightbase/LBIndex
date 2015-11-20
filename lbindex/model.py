#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'eduardo'

import logging
import config

import requests
from requests.exceptions import HTTPError

from liblightbase import lbrest
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbutils import conv
from liblightbase.lbsearch.search import *

logger = logging.getLogger("LBIndex")


class LogBase(object):
    """Base que contém o log de erros de indexação."""

    def __init__(self):
        """Método construtor."""

        self.rest_url = config.REST_URL
        self.baserest = lbrest.BaseREST(
            rest_url=self.rest_url,
            response_object=True
        )
        self.documentrest = lbrest.DocumentREST(
            rest_url=self.rest_url,
            base=self.lbbase,
            response_object=False
        )

    @property
    def lbbase(self):
        """Generate LB Base object
        :return:
        """

        nm_base = Field(**dict(
            name='nm_base',
            description='Nome da base',
            alias='Base',
            datatype='Text',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))

        dt_last_up_orig = Field(**dict(
            name='dt_last_up_orig',
            description='Data e Hora no formato DD/MM/AAAA - HH:MM:SS '
                        'da última atualização do registro que originou o erro.',
            alias='Data de Atualização',
            datatype='DateTime',
            indices=['Ordenado', 'Textual'],
            multivalued=False,
            required=True
        ))

        id_doc_orig = Field(**dict(
            name='id_doc_orig',
            description='ID do documento que originou o erro.',
            alias='Documento',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))

        error_msg = Field(**dict(
            name='error_msg',
            description='Mensagem de erro',
            alias='Mensagem',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=True
        ))

        dt_error = Field(**dict(
            name='dt_error',
            description='Data e Hora no formato DD/MM/AAAA - HH:MM:SS do erro',
            alias='Data do erro',
            datatype='DateTime',
            indices=['Textual', 'Ordenado'],
            multivalued=False,
            required=True
        ))

        content_list = Content()
        content_list.append(nm_base)
        content_list.append(dt_last_up_orig)
        content_list.append(id_doc_orig)
        content_list.append(error_msg)
        content_list.append(dt_error)

        base_metadata = BaseMetadata(**dict(
            name='log_lbindex',
            description='LightBase - Log de erros do LBIndex',
            password='123456',
            idx_exp=False,
            idx_exp_url='rest_url',
            idx_exp_time=300,
            file_ext=False,
            file_ext_time=300,
            color='#000000'
        ))

        lbbase = Base(
            metadata=base_metadata,
            content=content_list
        )

        return lbbase

    @property
    def metaclass(self):
        """Retorna metaclass para essa base."""

        return self.lbbase.metaclass()

    def create_base(self):
        """
        Create a base to hold twitter information on Lightbase
        :param crimes: One twitter crimes object to be base model
        :return: LB Base object
        """

        lbbase = self.lbbase
        self.baserest.response_object = True
        response = self.baserest.create(lbbase)
        if response.status_code == 200:
            return lbbase
        else:
            return None

    def remove_base(self):
        """
        Remove base from Lightbase
        :param lbbase: LBBase object instance
        :return: True or Error if base was not excluded
        """

        response = self.baserest.delete(self.lbbase)
        if response.status_code == 200:
            return True
        else:
            raise IOError('Error excluding base from LB')

    def update_base(self):
        """Update base from LB Base."""

        response = self.baserest.update(self.lbbase)
        if response.status_code == 200:
            return True
        else:
            raise IOError('Error updating LB Base structure')

    def get_document(self, id_doc):
        """
        Get document by ID on base
        """

        url = self.rest_url + '/' + self.lbbase.metadata.name + '/doc/' + id_doc
        response = requests.get(url)
        if response.status_code > 300:
            return None

        return response.json()

    def get_base(self):
        """
        Get base JSON
        """

        self.baserest.response_object = False
        try:
            response = self.baserest.get(self.lbbase)
            return True
        except HTTPError as e:
            logger.error("Base %s not found\n%s", self.lbbase.metadata.name, e.strerror)
            return False
