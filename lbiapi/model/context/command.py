# -*- coding: utf-8 -*-

import subprocess

from ..lbindex import LbIndex


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
        post_cmd_out = None

        if param_direct == "start":
            print("start")
            post_cmd_out = self.lb_index.start()
        elif param_direct == "stop":
            print("stop")
            post_cmd_out = self.lb_index.stop()
        elif param_direct == "restart":
            print("restart")
            post_cmd_out = self.lb_index.restart()
        elif param_direct == "status":
            print("status")
            post_cmd_out = self.lb_index.status()
        elif param_direct == "index":
            print("index")
            post_cmd_out = self.lb_index.index()
        elif param_direct == "cmd":
            print("cmd")
            if params.get("action", None):
                print(params["action"])
                post_cmd_out = self.lb_index.cmd(params["action"])
                pass
            else:
                print("Falta o parâmetro \"action\"!")
        else:
            print("Falta o parâmetro \"directive\"!")

        # TODO: Tratar esse retorno! By Questor
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
