# -*- coding: utf-8 -*-
"""Possuir variáveis globais cross-module.

Attributes:
    BASE_DIR (str): Constante com o caminho raiz do projeto.
    PY_BASE_DIR (str): Constante com o caminho base para o python que o 
        executa.

Essa solução permite acessar as variáveis de forma mais simples e entre os 
módulos passando o nome da variável com o caminho do módulo. Better because it 
avoids possible namespace conflicts. Ref.: 
http://stackoverflow.com/questions/142545/python-how-to-make-a-cross-module-variable
"""

BASE_DIR=""

PY_BASE_DIR=""
