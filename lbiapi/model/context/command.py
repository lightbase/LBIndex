#!/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from pyramid.renderers import render_to_response


class CommandFactory():
    """??????????????????????????????"""

    def __init__(self, request):
        self.request = request
        pass

    def post_command(self):
        """??????????????????????????????"""

        # print("post_command")
        renderer = "../../templates/mytemplate.pt"
        return render_to_response(
            renderer, 
            {'project': 'LBIApi'}, 
            request=self.request)

    def get_command(self):
        """??????????????????????????????"""

        # print("get_command")
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

    def put_command(self):
        """??????????????????????????????"""

        # print("put_command")
        renderer = "../../templates/mytemplate.pt"
        return render_to_response(
            renderer, 
            {'project': 'LBIApi'}, 
            request=self.request)

    def delete_command(self):
        """??????????????????????????????"""

        # print("delete_command")
        renderer = "../../templates/mytemplate.pt"
        return render_to_response(
            renderer, 
            {'project': 'LBIApi'}, 
            request=self.request)