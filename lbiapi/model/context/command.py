# -*- coding: utf-8 -*-

import subprocess

from ..lbindex import LbIndex
from ...lib.httpcode import HTTPCode
from ...lib.exception import HTTPServiceException

class CommandFactory():
    """Tratar o factory referente aos comandos.

    Args:
        request (pyramid.request.Request): Request gerado pelo pacote 
            Pyramid.

    Attributes:
        lb_index (LbIndex): Composição com a classe para controle do LBI.

    Returns:
        CommandFactory: Instância de CommandFactory.
    """

    def __init__(self, request):
        self.request = request
        self.lb_index = LbIndex(request)

    def post_command(self, params):
        """Tratar o verbo HTTP POST."""

        param_direct = params.get("directive", None)
        if len(params) > 2 or (len(params) == 2 and param_direct != "cmd"):
            raise HTTPServiceException(HTTPCode().CODE400, "Too many fields!")

        if not param_direct:
            raise HTTPServiceException(
                HTTPCode().CODE400, 
                "The \"directive\" field is missing or incorrect!")

        post_cmd_out = None
        if param_direct == "start":
            post_cmd_out = self.lb_index.start()
        elif param_direct == "stop":
            post_cmd_out = self.lb_index.stop()
        elif param_direct == "restart":
            post_cmd_out = self.lb_index.restart()
        elif param_direct == "status":
            post_cmd_out = self.lb_index.status()
        elif param_direct == "index":
            post_cmd_out = self.lb_index.index()
        elif param_direct == "cmd":
            try:
                action_value = params["action"]
            except Exception as e:
                raise HTTPServiceException(
                    HTTPCode().CODE400, 
                    "The \"action\" field is missing or incorrect!")
            if action_value:
                print(params["action"])
                post_cmd_out = self.lb_index.cmd(params["action"])
                pass
            else:
                raise HTTPServiceException(
                    HTTPCode().CODE400, 
                    "The \"action\" field does not have a valid value!")
        else:
            raise HTTPServiceException(
                HTTPCode().CODE400, 
                "The \"directive\" field does not have a valid value!")

        return post_cmd_out

    def get_command(self):
        """Tratar o verbo HTTP GET."""

        return None

    def put_command(self):
        """Tratar o verbo HTTP PUT."""

        return None

    def delete_command(self):
        """Tratar o verbo HTTP DELETE."""

        return None
