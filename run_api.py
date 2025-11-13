#!/usr/bin/env python3
"""
Script para iniciar o servidor API
"""
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api import run_api_server

if __name__ == "__main__":
    run_api_server()
