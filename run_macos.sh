#!/bin/bash
#
# Script para rodar a aplicação no macOS
#

echo "=========================================="
echo " Apple Music to iCUE LCD - macOS"
echo "=========================================="
echo ""

# Verifica se está no macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script é apenas para macOS"
    exit 1
fi

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    echo "Instale com: brew install python3"
    exit 1
fi

# Verifica se o Apple Music está rodando
if ! pgrep -x "Music" > /dev/null; then
    echo "⚠️  Apple Music não está rodando"
    echo "Abrindo Apple Music..."
    open -a "Music"
    sleep 2
fi

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verifica dependências
echo "Verificando dependências..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Instalando dependências..."
    pip3 install -r requirements.txt
fi

# Carrega configurações do .env ou usa mock
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado, usando configurações padrão"
    export USE_MOCK_ICUE=True
fi

echo ""
echo "🚀 Iniciando aplicação..."
echo "   Modo: Mock iCUE (sem hardware)"
echo "   Pressione Ctrl+C para parar"
echo ""

# Força modo mock no macOS (a menos que tenha iCUE instalado)
export USE_MOCK_ICUE=True

# Executa a aplicação
python3 run.py
