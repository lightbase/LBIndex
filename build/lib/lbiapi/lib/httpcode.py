# -*- coding: utf-8 -*-
"""Tratar e normalizar o retorno HTML para esta aplicação."""


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
