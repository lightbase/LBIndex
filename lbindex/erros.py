#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger("LBIndex")

# class Error(Exception):
#     """Classe base para erros"""
#     pass


# class RequestError(Error):
#     """Exception para quando a aplicação rest retornar um erro."""


#     def __init__(self, prev, next, msg):
#         self.prev = prev
#         self.next = next
#         self.msg = msg


def is_error(json_resp):
    erro = '_status' in json_resp and '_error_message' in json_resp and \
           '_request' in json_resp and '_path' in json_resp and \
           len(json_resp) == 4
    return erro

def errorest(json_resp):
    logger.error(str(json_resp['_status']) + ': ' +\
                 json_resp['_error_message'])