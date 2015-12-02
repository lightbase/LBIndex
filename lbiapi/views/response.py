#!/bin/env python
# -*- coding: utf-8 -*-

from pyramid.renderers import render_to_response


class HTTPCode():
    """????????????????????????????????????????"""

    def __init__(self):

        # 1xx Informational
        self.code100 = (100, "Continue.")
        self.code101 = (101, "Switching Protocols.")
        self.code102 = (102, "Processing.")

        # 2xx Success
        self.code200 = (200, "OK.")
        self.code201 = (201, "Created.")
        self.code202 = (202, "Accepted.")
        self.code203 = (203, "Non-Authoritative Information.")
        self.code204 = (204, "No Content.")
        self.code205 = (205, "Reset Content.")
        self.code206 = (206, "Partial Content.")
        self.code207 = (207, "Multi-Status.")
        self.code208 = (208, "Already Reported.")
        self.code226 = (226, "IM Used.")

        # 3xx Redirection
        self.code300 = (300, "Multiple Choices.")
        self.code301 = (301, "Moved Permanently.")
        self.code302 = (302, "Found.")
        self.code303 = (303, "See Other.")
        self.code304 = (304, "Not Modified.")
        self.code305 = (305, "Use Proxy.")
        self.code306 = (306, "Switch Proxy.")
        self.code307 = (307, "Temporary Redirect.")
        self.code308 = (308, "Permanent Redirect.")
        self.code308 = (308, "Resume Incomplete.")

        # 4xx Client Error
        self.code400 = (400, "Bad Request.")
        self.code401 = (401, "Unauthorized.")
        self.code402 = (402, "Payment Required.")
        self.code403 = (403, "Forbidden.")
        self.code404 = (404, "Not Found.")
        self.code405 = (405, "Method Not Allowed.")
        self.code406 = (406, "Not Acceptable.")
        self.code407 = (407, "Proxy Authentication Required.")
        self.code408 = (408, "Request Timeout.")
        self.code409 = (409, "Conflict.")
        self.code410 = (410, "Gone.")
        self.code411 = (411, "Length Required.")
        self.code412 = (412, "Precondition Failed.")
        self.code413 = (413, "Payload Too Large.")
        self.code414 = (414, "URI Too Long.")
        self.code415 = (415, "Unsupported Media Type.")
        self.code416 = (416, "Range Not Satisfiable.")
        self.code417 = (417, "Expectation Failed.")
        self.code418 = (418, "I'm a teapot.")
        self.code419 = (419, "Authentication Timeout.")
        self.code420 = (420, "Method Failure.")
        self.code421 = (421, "Misdirected Request.")
        self.code422 = (422, "Unprocessable Entity.")
        self.code423 = (423, "Locked.")
        self.code424 = (424, "Failed Dependency.")
        self.code426 = (426, "Upgrade Required.")
        self.code449 = (449, "Retry With.")
        self.code450 = (450, "Blocked by Windows Parental Controls.")
        self.code451 = (451, "Unavailable For Legal Reasons.")
        self.code498 = (498, "Token expired/invalid.")
        self.code499 = (499, "Client Closed Request.")

        # 5xx Server Error
        self.code500 = (500, "Internal Server Error.")
        self.code501 = (501, "Not Implemented.")
        self.code502 = (502, "Bad Gateway.")
        self.code503 = (503, "Service Unavailable.")
        self.code504 = (504, "Gateway Timeout.")
        self.code505 = (505, "HTTP Version Not Supported.")
        self.code506 = (506, "Variant Also Negotiates.")
        self.code507 = (507, "Insufficient Storage.")
        self.code508 = (508, "Loop Detected.")
        self.code509 = (509, "Bandwidth Limit Exceeded.")
        self.code510 = (510, "Not Extended.")
        self.code598 = (598, "Network read timeout error.")
        self.code599 = (599, "Network connect timeout error.")

        # Rapid use!
        self.success = self.code200
        self.warning = self.code400
        self.error = self.code500

class Cmd(object):
    """????????????????????????"""

    def __init__(self, result, code=HTTPCode, message=None):

        # NOTE: ????????????????????! By Questor
        if not message:
            message = code[1]

        self._cmd_resp = {
            'code': code[0],
            'message': message,
            'level': self.get_level(code[0]),
            'result': result
        }

    @property
    def cmd_resp(self):
        return self._cmd_resp

    def get_level(self, code):
        """????????????????????????????????????????"""

        success = [100, 102, 200, 201, 202, 207]
        warning = [101, 203, 204, 205, 206, 208, 226, 300, 301, 302, 303, 
            304, 305, 306, 307, 308, 308]
        error = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 
            411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 
            423, 424, 426, 449, 450, 451, 498, 499, 500, 501, 502, 503, 
            504, 505, 506, 507, 508, 509, 510, 598, 599]
        if code in success:
            return "success"
        if code in warning:
            return "warning"
        if code in error:
            return "error"

class Response(object):
    """????????????????????????"""

    def __init__(self):
        self._cmds = []
        self._http_code = None
        self.http_codes = HTTPCode()

    @property
    def http_code(self):
        if not self._http_code:
            return self.http_codes.code200
        return self._http_code

    @http_code.setter
    def http_code(self, value=HTTPCode):
        self._http_code = value

    @property
    def cmds(self):
        return self._cmds

    @cmds.setter
    def cmds(self, value=Cmd):
        self._cmds.append(value.cmd_resp)

    def render_response(self):
        """????????????????????????????????????????"""

        render_response_out = {'http': {}, 'cmds': self.cmds}

        # NOTE: ?????????????????????????????????????! By Questor
        render_response_out['http'] = {
            'code': self.http_code[0],
            'message': self.http_code[1],
        }

        return render_to_response(
            "def_json_rend", 
            render_response_out, 
            request=self.request)
