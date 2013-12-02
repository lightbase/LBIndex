# -*- coding: utf-8 -*-

import logging
import lbrest
import config

def main():

    logger.info ('Iniciando rotina indexacao ...')
    bases = lbrest.get_bases()
    if bases:
        for _base in bases:
            id = _base['id_base']
            base = _base['nome_base']
            index_time = _base['index_time']
            index_url = _base['nome_base']

            base_json = lbrest.get_base_json(id)
            if base_json:

                logger.info('Comecando indexacao da base %s ...' % base)
                registries = lbrest.get_registries(base)
                if registries:
                    index_registries(base, base_json, registries)
                else:
                    logger.info('Nenhum registro encontrado.')

def index_registries(base, base_json, registries):

    for registry in registries:
        id = registry['id_reg']
        full_reg = lbrest.get_full_reg(base, id)
        if full_reg:
            indexed = lbrest.index_member(base, base_json, full_reg, id)
            if indexed:
                lbrest.update_dt_index(base, id)

logger = logging.getLogger("LBIndex")

