# -*- coding: utf-8 -*-

from pyramid.renderers import render_to_response
from response import Response
from ..lib.httpcode import HTTPCode

class CustomView(Response):
    """Visão padrão do sistema.

    Herdada por todas as demais.
    Extende Response.

    Args:
        context (instance): Instância do contexto à ser usado com a view.
        request (pyramid.request.Request): Request gerado pelo pacote 
            Pyramid.

    Returns:
        CustomView: Instância de CustomView.
    """

    def __init__(self, context, request):
        super(CustomView, self).__init__()
        self.context = context
        self.request = request

    def split_req(self, request):
        """Separar os parâmetros da requisição e o verbo HTTP.

        Args:
            request (pyramid.request.Request): Request gerado pelo pacote 
                Pyramid.

        Returns:
            (dict[webob.multidict.NestedMultiDict], str): Tupla com os 
                parâmetros da requisição e o verbo HTTP.
        """

        return dict(request.params), request.method
