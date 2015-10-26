#!/bin/env python
# -*- coding: utf-8 -*-

from pyramid.renderers import render_to_response

class CustomView():
    """Default customized view methods."""

    def cmd_resp(self):

        cmd_resp_out = {'overall': {}, 'results': self.rtn_values}

        if self.code > 400:
            cmd_resp_out['overall'] = {
                'http_code': self.code,
                'status': self.status,
                'context': self.context_,
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
                'context': self.context_
            }

        return render_to_response(
            "def_json_rend", 
            cmd_resp_out, 
            request=self.request)