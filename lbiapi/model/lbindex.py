# -*- coding: utf-8 -*-
"""Tratar as operações com o LBI."""

import os
import time
import tempfile
import subprocess

from .. globals import BASE_DIR


class LbIndex():
    """API para o o serviço LBI.

    Args:
        request (pyramid.request.Request): Request gerado pelo pacote 
            Pyramid.

    Attributes:
        request (pyramid.request.Request): Request atual gerado pelo pacote 
            Pyramid..

    Returns:
        LbIndex: Instância de LbIndex.
    """

    def __init__(self, request):
        self.request = request
        pass

    def start(self):
        """Iniciar o serviço LBI.

        Returns:
            str: Retorno do LBI.
        """

        cmd_vl = ["/usr/local/lbneo/virtenvlb2.6/bin/python", "lbindex", "start"]
        output = self.ez_subprocess(cmd_vl)
        return output

    def stop(self):
        """Parar o serviço LBI.

        Returns:
            str: Retorno do LBI.
        """

        cmd_vl = ["/usr/local/lbneo/virtenvlb2.6/bin/python", "lbindex", "stop"]
        output = self.ez_subprocess(cmd_vl)
        return output

    def status(self):
        """Status do serviço LBI.

        Returns:
            str: Retorno do LBI.
        """

        cmd_vl = ["/usr/local/lbneo/virtenvlb2.6/bin/python", "lbindex", "status"]
        output = self.ez_subprocess(cmd_vl)
        return output

    def restart(self):
        """Reiniciar o serviço LBI.

        Returns:
            str: Retorno do LBI.
        """

        cmd_vl = ["/usr/local/lbneo/virtenvlb2.6/bin/python", "lbindex", "restart"]
        output = self.ez_subprocess(cmd_vl)
        return output

    def index(self):
        """Disparar a indexação no serviço LBI.

        Returns:
            str: Retorno do LBI.
        """

        cmd_vl = ["/usr/local/lbneo/virtenvlb2.6/bin/python", "lbindex", "index"]
        output = self.ez_subprocess(cmd_vl)
        return output

    def cmd(self, action):
        """Passar comandos específicos para o LBI.

        Args:
            action (str): Valor do comando a ser passado para o LBI.

        Returns:
            str: Retorno do LBI.
        """

        cmd_vl = ["/usr/local/lbneo/virtenvlb2.6/bin/python", "lbindex", "cmd", "-a", action]
        output = self.ez_subprocess(cmd_vl)
        return output

    def ez_subprocess(self, cmd_vl):
        """Facilitar criar subprocessos sem bloquer o serviço HTTP.

        Args:
            cmd_vl (str): Valor do argumento a ser passado para o LBI.

        Returns:
            str: Retorno do LBI ("stderr" e "stdout").
        """

        # NOTE: Usamos arquivos para "stderr" e "stdout" para que a não 
        # existência de um dos dois no bloqueie a saída. Nesse esquema 
        # esperamos até 10 segundos pelo retorno, caso contrário mata o 
        # processo! By Questor
        outFile = tempfile.SpooledTemporaryFile()
        errFile = tempfile.SpooledTemporaryFile()
        proc = subprocess.Popen(cmd_vl, 
                                # shell=True, 
                                stderr=errFile, 
                                stdout=outFile, 
                                universal_newlines=False,
                                cwd=BASE_DIR)
        wait_remaining_sec = 10

        while proc.poll() is None and wait_remaining_sec > 0:
            time.sleep(1)
            wait_remaining_sec -= 1

        if wait_remaining_sec <= 0:
            # TODO: Tratar erro! By Questor
            print("The service does not respond!")

        # NOTE: Read temp streams from start! By Questor
        outFile.seek(0);
        errFile.seek(0);
        out = outFile.read()
        err = errFile.read()
        outFile.close()
        errFile.close()

        # NOTE: Trata-se de um workaround para a saída do o serviço LBI. 
        # Por alguma razão o valor "stdout" vem repetido 3 vêses 
        # quando cpturado por "Popen" em determinadas circunstâncias! 
        # By Questor
        if out == "Starting daemon ...\nStarting daemon ...\nStarting daemon ...\n":
            out = "Starting daemon ..."
        if out == "Restarting daemon ...\nRestarting daemon ...\nRestarting daemon ...\n":
            out = "Restarting daemon ..."

        # NOTE: To debug! By Questor
        # print(str(out))
        # print(str(err))

        return out + err
