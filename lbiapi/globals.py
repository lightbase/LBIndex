# -*- coding: utf-8 -*-
"""Setar as variáveis globais BASE_DIR e PY_BASE_DIR que contém o diretório 
dos arquivos deste projeto e o caminho para o python que o executa."""

import os
import sys

global BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

global PY_BASE_DIR
PY_BASE_DIR = sys.path[1].split("/lib/")[0] + "/bin/python"
