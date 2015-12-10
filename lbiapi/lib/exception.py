# -*- coding: utf-8 -*-

from httpcode import HTTPCode


class HTTPServiceException(Exception):

    def __init__(self, http_code=HTTPCode, e_msg=""):
        Exception.__init__(self, http_code, e_msg)
