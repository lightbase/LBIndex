#!/bin/env python
# -*- coding: utf-8 -*-

from pyramid.renderers import render_to_response
from response import Response
from response import HTTPCode

class CustomView(Response):
    """Default customized view methods."""

    def __init__(self, context, request):
        super(CustomView, self).__init__()
        self.context = context
        self.request = request
        # self.http_codes = HTTPCode()
        # self.response = Response()

    def split_req(self, request):
        return dict(request.params), request.method
