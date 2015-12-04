# -*- coding: utf-8 -*-
"""Tratar e normalizar o retorno HTML para esta aplicação."""

from pyramid.renderers import render_to_response


class HTTPCode():
    """Padronizar os códigos de status HTTP e suas descrições.

    A idéia é que seus atributos sejam usados como um enum.
    """

    def __init__(self):

        # 1xx Informational
        self.CODE100 = (100, "Continue.")
        self.CODE101 = (101, "Switching Protocols.")
        self.CODE102 = (102, "Processing.")

        # 2xx Success
        self.CODE200 = (200, "OK.")
        self.CODE201 = (201, "Created.")
        self.CODE202 = (202, "Accepted.")
        self.CODE203 = (203, "Non-Authoritative Information.")
        self.CODE204 = (204, "No Content.")
        self.CODE205 = (205, "Reset Content.")
        self.CODE206 = (206, "Partial Content.")
        self.CODE207 = (207, "Multi-Status.")
        self.CODE208 = (208, "Already Reported.")
        self.CODE226 = (226, "IM Used.")

        # 3xx Redirection
        self.CODE300 = (300, "Multiple Choices.")
        self.CODE301 = (301, "Moved Permanently.")
        self.CODE302 = (302, "Found.")
        self.CODE303 = (303, "See Other.")
        self.CODE304 = (304, "Not Modified.")
        self.CODE305 = (305, "Use Proxy.")
        self.CODE306 = (306, "Switch Proxy.")
        self.CODE307 = (307, "Temporary Redirect.")
        self.CODE308 = (308, "Permanent Redirect.")
        self.CODE308 = (308, "Resume Incomplete.")

        # 4xx Client Error
        self.CODE400 = (400, "Bad Request.")
        self.CODE401 = (401, "Unauthorized.")
        self.CODE402 = (402, "Payment Required.")
        self.CODE403 = (403, "Forbidden.")
        self.CODE404 = (404, "Not Found.")
        self.CODE405 = (405, "Method Not Allowed.")
        self.CODE406 = (406, "Not Acceptable.")
        self.CODE407 = (407, "Proxy Authentication Required.")
        self.CODE408 = (408, "Request Timeout.")
        self.CODE409 = (409, "Conflict.")
        self.CODE410 = (410, "Gone.")
        self.CODE411 = (411, "Length Required.")
        self.CODE412 = (412, "Precondition Failed.")
        self.CODE413 = (413, "Payload Too Large.")
        self.CODE414 = (414, "URI Too Long.")
        self.CODE415 = (415, "Unsupported Media Type.")
        self.CODE416 = (416, "Range Not Satisfiable.")
        self.CODE417 = (417, "Expectation Failed.")
        self.CODE418 = (418, "I'm a teapot.")
        self.CODE419 = (419, "Authentication Timeout.")
        self.CODE420 = (420, "Method Failure.")
        self.CODE421 = (421, "Misdirected Request.")
        self.CODE422 = (422, "Unprocessable Entity.")
        self.CODE423 = (423, "Locked.")
        self.CODE424 = (424, "Failed Dependency.")
        self.CODE426 = (426, "Upgrade Required.")
        self.CODE449 = (449, "Retry With.")
        self.CODE450 = (450, "Blocked by Windows Parental Controls.")
        self.CODE451 = (451, "Unavailable For Legal Reasons.")
        self.CODE498 = (498, "Token expired/invalid.")
        self.CODE499 = (499, "Client Closed Request.")

        # 5xx Server Error
        self.CODE500 = (500, "Internal Server Error.")
        self.CODE501 = (501, "Not Implemented.")
        self.CODE502 = (502, "Bad Gateway.")
        self.CODE503 = (503, "Service Unavailable.")
        self.CODE504 = (504, "Gateway Timeout.")
        self.CODE505 = (505, "HTTP Version Not Supported.")
        self.CODE506 = (506, "Variant Also Negotiates.")
        self.CODE507 = (507, "Insufficient Storage.")
        self.CODE508 = (508, "Loop Detected.")
        self.CODE509 = (509, "Bandwidth Limit Exceeded.")
        self.CODE510 = (510, "Not Extended.")
        self.CODE598 = (598, "Network read timeout error.")
        self.CODE599 = (599, "Network connect timeout error.")

        # Rapid use!
        self.success = self.CODE200
        self.warning = self.CODE400
        self.error = self.CODE500

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
        http_code (HTTPCode) = Código de status HTTP da requisição atual.
        more_info (Optional[str]): Informação adicional sobre a operação ou 
            problema. Padrão "".

    Returns:
        Response: Instância de Response.
    """

    def __init__(self):
        self._cmds = []
        self._http_code = None
        self.more_info = ""

        # NOTE: Como o tipo HTTPCode é intrinsecamente ligado ao 
        # retorno da aplicação, fiz composição com a classe 
        # Response! By Questor
        self.http_codes = HTTPCode()

    @property
    def http_code(self):
        """HTTPCode: Retornar o código setado para a resposta HTML.

        Se não houver código HTML setado retorna o código padrão.
        """
        if not self._http_code:
            return self.http_codes.CODE200
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

    if len(cmds) == 1:
        response.status = str(status_code) + " " + status_msg
    return response
