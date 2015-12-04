# -*- coding: utf-8 -*-

from ..views.response import HTTPCode


class HTTPServiceException(Exception):

    def __init__(self, http_code=HTTPCode, e_msg=""):
        Exception.__init__(self, http_code, e_msg)
