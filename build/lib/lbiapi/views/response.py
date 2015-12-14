# -*- coding: utf-8 -*-
"""Tratar e normalizar o retorno HTML para esta aplicação."""

from pyramid.renderers import render_to_response
from ..lib.httpcode import HTTPCode


class Cmd(object):
    """Comportar o retorno individual de cada comando.

    Garantir a integridade do retorno do tipo Cmd.

    Args:
        result (str, dict): Saída do comando.
        status_code (HTTPCode): Código HTTP.
        more_info (Optional[str]): Informação adicional sobre a operação ou 
            problema. Padrão "".

    Returns:
        Cmd: Instância de Cmd.
    """

    def __init__(self, result, http_code=HTTPCode, more_info=""):

        self._cmd_resp = {
            'status_code': http_code[0],
            'status_msg': http_code[1],
            'more_info': more_info,
            'level': self.get_level(http_code[0]),
            'result': result
        }

    @property
    def cmd_resp(self):
        """dict: Retornar o dict referente ao tipo Cmd."""
        return self._cmd_resp

    def get_level(self, status_code):
        """Define um "level" para o retorno conforme o código HTTP setado.

        Visa facilitar a leitura do retorno no "client side".

        Args:
            status_code (int): Código HTTP.

        Returns:
            str: Level.
        """

        success = [100, 102, 200, 201, 202, 207]
        warning = [101, 203, 204, 205, 206, 208, 226, 300, 301, 302, 303, 
            304, 305, 306, 307, 308, 308]
        error = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 
            411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 
            423, 424, 426, 449, 450, 451, 498, 499, 500, 501, 502, 503, 
            504, 505, 506, 507, 508, 509, 510, 598, 599]
        if status_code in success:
            return "success"
        if status_code in warning:
            return "warning"
        if status_code in error:
            return "error"

class Response(object):
    """Tratar o retorno HTML.

    Attributes:
        cmds (list): Lista de todos os comandos solicitados na requisição 
            HTTP atual.
        more_info (Optional[str]): Informação adicional sobre a operação ou 
            problema. Padrão "".

    Returns:
        Response: Instância de Response.
    """

    def __init__(self):
        self._cmds = []
        self._http_code = None
        self.more_info = ""

    @property
    def http_code(self):
        """HTTPCode: Retornar o código setado para a resposta HTML.

        Se não houver código HTML setado retorna o código padrão.
        """
        if not self._http_code:
            return HTTPCode().CODE200
        return self._http_code

    @http_code.setter
    def http_code(self, value=HTTPCode):
        self._http_code = value

    @property
    def cmds(self):
        """List[dict]: Retornar a lista de comandos na operação atual."""
        return self._cmds

    @cmds.setter
    def cmds(self, value=Cmd):
        self._cmds.append(value.cmd_resp)

    def render_response(self):
        """Gerar o retorno HTML. 

        Após setados todos os retornos de cada comando.
        """

        render_response_out = {'http': {}, 'cmds': self.cmds}
        status_code = self.http_code[0]
        status_msg = self.http_code[1]
        more_info = self.more_info

        return finally_render(self.request, 
                              status_code, 
                              status_msg, 
                              more_info, 
                              self.cmds)

def finally_render(request, status_code, status_msg, more_info, cmds):
    """?????????????????????????????"""

    render_response_out = {'http': {}, 'cmds': cmds}

    # NOTE: Para que a aplicação tenha um nível mais elaborado 
    # de integração com o modelo HTTP, quando é enviado apenas 
    # um comando o código de retorno é integrado ao próprio 
    # retorno HTML! By Questor
    if len(cmds) == 1:
        status_code = cmds[0]["status_code"]
        status_msg = cmds[0]["status_msg"]
        more_info = cmds[0]["more_info"]

    # NOTE: Trata-se do retorno principal da requisição. Esse 
    # status sempre coincide com o status do próprio retorno 
    # HTML! By Questor
    render_response_out['http'] = {
        'status_code': status_code,
        'status_msg': status_msg,
        'more_info': more_info
    }

    response = render_to_response(
        "def_json_rend", 
        render_response_out, 
        request=request)

    if len(cmds) <= 1:
        response.status = str(status_code) + " " + status_msg
    return response
