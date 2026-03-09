#!/usr/bin/env python3
"""
Launcher para AIContext Toolkit
"""

import sys
import os

# Adicionar diretório atual ao PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar e executar o main
from aicontext_toolkit import __main__ as main_module

if __name__ == "__main__":
    main_module.main()
