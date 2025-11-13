#!/bin/bash
#
# Script de teste para macOS
#

echo "=========================================="
echo " Apple Music to iCUE LCD - Teste macOS"
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

echo "✅ Python $(python3 --version) encontrado"

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

echo ""
echo "=========================================="
echo " Testando Monitor do Apple Music"
echo "=========================================="
echo ""
echo "▶️  Toque uma música no Apple Music para ver os resultados"
echo "⏹️  Pressione Ctrl+C para parar"
echo ""

# Define mock do iCUE para testes
export USE_MOCK_ICUE=True

# Testa o monitor
python3 src/apple_music_monitor_macos.py
