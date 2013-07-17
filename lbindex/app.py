#!/usr/bin/python
# -*- coding: utf-8 -*-
from scripts import buscabases
from scripts import buscaregistro
from scripts import indexa

import logging

logger = logging.getLogger("LBIndex")

def main(domain, elastic, force):
    bases = buscabases.listarbases(domain)
    (listabases, listaregs) = buscaregistro.listarregistros(domain, bases,
                                                            force)
    if len(listaregs) == 0:
        logger.info('Não existem registros para serem indexados')
    else:
        logger.info('Iniciando indexação de ' + str(len(listaregs)) +\
                    ' registros')
        indexa.indexar(domain, elastic, listabases, listaregs)