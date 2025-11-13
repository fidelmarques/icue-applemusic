#!/bin/bash
#
# Script para testar detecção de capas animadas
#

echo "=========================================="
echo " Teste de Capas Animadas - Apple Music"
echo "=========================================="
echo ""

# Verifica se está no macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script é apenas para macOS"
    exit 1
fi

echo "📖 Como funciona:"
echo "   - Músicas com capa animada têm múltiplos frames"
echo "   - O sistema detecta e prioriza automaticamente"
echo ""
echo "🎵 Para testar:"
echo "   1. Toque uma música com Apple Music Animated Cover"
echo "   2. O script mostrará se é animada ou estática"
echo ""
echo "💡 Dica: Nem todas as músicas têm capa animada!"
echo "   Procure por álbuns recentes no Apple Music"
echo ""
echo "▶️  Iniciando monitoramento..."
echo "⏹️  Pressione Ctrl+C para parar"
echo ""

# Define mock do iCUE para testes
export USE_MOCK_ICUE=True

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Testa o monitor
python3 src/apple_music_monitor_macos.py
