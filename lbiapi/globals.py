# -*- coding: utf-8 -*-
"""Setar a variável global BASE_DIR."""

import os
import sys

global BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

global PY_BASE_DIR
PY_BASE_DIR = sys.path[1].split("/lib/")[0] + "/bin/python"
