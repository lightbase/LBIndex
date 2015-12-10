# -*- coding: utf-8 -*-

from . import CustomView
from response import Cmd
from error import HTTPServiceException
from response import HTTPCode

class CommandView(CustomView):
    """Tratar a visão referente aos comandos.

    Extende CustomView.

    Args:
        context (instance): Instância do contexto à ser usado com a view.
        request (pyramid.request.Request): Request gerado pelo pacote 
            Pyramid.

    Returns:
        CommandView: Instância de CommandView.
    """

    def __init__(self, context, request):
        super(CommandView, self).__init__(context, request)

    def post_command(self):
        """Tratar o verbo HTTP POST."""

        # try:
            # # test = 2/0
            # test = 2/2
        # except Exception as e:
            # raise HTTPServiceException(HTTPCode().CODE500, str(e))

        params, method = self.split_req(self.request)
        result = self.context.post_command(params)
        cmds = Cmd(result, HTTPCode().CODE200)
        self.cmds = cmds

        return self.render_response()

    def get_command(self):
        """Tratar o verbo HTTP GET."""

        raise HTTPServiceException(HTTPCode().CODE501)

    def put_command(self):
        """Tratar o verbo HTTP PUT."""

        raise HTTPServiceException(HTTPCode().CODE501)

    def delete_command(self):
        """Tratar o verbo HTTP DELETE."""

        raise HTTPServiceException(HTTPCode().CODE501)
