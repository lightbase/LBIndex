#!/bin/env python
# -*- coding: utf-8 -*-

from pyramid.renderers import render_to_response


class CustomView(object):
    """Default customized view methods."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.code = 200
        self.status = "success"
        self.scope = "result"
        self.rtn_vals = []
        self.error_message = ""
        pass

    def cmd_resp(self):

        cmd_resp_out = {'overall': {}, 'results': self.rtn_vals}

        if self.code > 400:
            cmd_resp_out['overall'] = {
                'http_code': self.code,
                'status': self.status,
                'scope': self.scope,
                'error_msg': self.error_message,
                'request': {
                        'client_addr': self.request.client_addr,
                        'user_agent': self.request.user_agent,
                        'path': getattr(self.request, 'path', 'Not avalible'),
                        'method': self.request.method
                    }
            }
        else:
            cmd_resp_out['overall'] = {
                'http_code': self.code,
                'status': self.status,
                'context': self.scope
            }

        return render_to_response(
            "def_json_rend", 
            cmd_resp_out, 
            request=self.request)

    def split_req(self, request):
        return dict(request.params), request.method
