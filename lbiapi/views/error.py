# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.renderers import render_to_response

from .response import finally_render
from ..lib.exception import HTTPServiceException

def http_service_exception(response_args, request):

    status_code = response_args[0][0]
    status_msg = response_args[0][1]
    more_info = response_args[1]
    cmds = []

    return finally_render(request, 
                          status_code, 
                          status_msg, 
                          more_info, 
                          cmds)
