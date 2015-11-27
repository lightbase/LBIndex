#!/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import fcntl, os
import tempfile
import time

class LbIndex():
    """??????????????????????????????"""

    def __init__(self, request):
        self.request = request
        pass

    def stop(self):
        """??????????????????????????????"""

        popen_out = subprocess.Popen(
            "cd /usr/local/lbneo/virtenvlb2.6/src/"\
            "LBIndex && /usr/local/lbneo/virtenvlb2.6/bin/python "\
            "lbindex stop", 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
        out, err = popen_out.communicate()

        output = ""
        if out:
            output = out
        if err:
            output = output + err

        return output

    def start(self):
        """??????????????????????????????"""

        outFile = tempfile.SpooledTemporaryFile()
        errFile = tempfile.SpooledTemporaryFile()
        proc = subprocess.Popen("cd /usr/local/lbneo/virtenvlb2.6/src/"\
                "LBIndex && /usr/local/lbneo/virtenvlb2.6/bin/python "\
                "lbindex start", shell=True, stderr=errFile, stdout=outFile, universal_newlines=False)
        wait_remaining_sec = 10



        # TODO: Tentar stdout=outFile PIPED e stderr=errFile não! By Questor



        while proc.poll() is None and wait_remaining_sec > 0:
            time.sleep(1)
            wait_remaining_sec -= 1

        if wait_remaining_sec <= 0:
            killProc(proc.pid)
            raise ProcessIncompleteError(proc, timeout)

        # read temp streams from start
        outFile.seek(0);
        errFile.seek(0);
        out = outFile.read()
        err = errFile.read()
        outFile.close()
        errFile.close()

        print(str(out))
        print(str(err))
        output = out + err

        return output
