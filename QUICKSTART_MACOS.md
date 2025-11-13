# 🚀 Quick Start - macOS

Guia rápido para começar a testar no macOS em 5 minutos!

## 📦 Instalação Express

```bash
# 1. Clone o repositório
git clone https://github.com/fidelmarques/icue-applemusic.git
cd icue-applemusic

# 2. Instale dependências
pip3 install -r requirements.txt

# 3. Configure (opcional)
cp .env.example .env
```

## 🎵 Teste Rápido (30 segundos)

```bash
# 1. Abra o Apple Music e toque uma música!
open -a "Music"

# 2. Execute o teste
./test_macos.sh
```

Você verá algo como:

```
🎵 Tocando agora:
   Título: Bohemian Rhapsody
   Artista: Queen
   Álbum: A Night at the Opera
   Duração: 354s
   Posição: 42s
   ✅ Artwork salva em /tmp/test_artwork.jpg
```

## 🖼️ Ver a Capa Processada

```bash
# Abrir a última capa salva
open /tmp/test_artwork.jpg
```

## 🔥 Rodar a Aplicação Completa

```bash
# Executa com todas as funcionalidades (modo mock)
./run_macos.sh
```

Saída esperada:

```
========================================
 Apple Music to iCUE LCD - macOS
========================================

✅ Monitor do Apple Music inicializado (macOS)
✅ Processador de imagens inicializado
✅ Mock iCUE Controller inicializado (sem hardware)

🚀 Aplicação iniciada!
   Intervalo de atualização: 2.0s
   Duração do fade: 1.0s

🎵 Nova música detectada: Artist - Title
🖼️  Atualizando display com fade...
Mock: Fade transition (1.0s @ 30fps)
```

## 🌐 Testar API REST

```bash
# Terminal 1: Iniciar servidor
python3 run_api.py

# Terminal 2: Testar endpoints
curl http://localhost:5000/status
curl http://localhost:5000/current
```

## 📸 Ver Capas em Cache

```bash
# Listar capas processadas
ls -lht cache/

# Abrir uma capa específica
open cache/Queen_A_Night_at_the_Opera.png
```

## 🎨 Exemplo Completo

```bash
#!/bin/bash

# 1. Abrir Apple Music
open -a "Music"
echo "▶️  Toque uma música no Apple Music!"
sleep 3

# 2. Testar monitor
echo "🧪 Testando monitor..."
timeout 10 python3 src/apple_music_monitor_macos.py

# 3. Rodar aplicação
echo "🚀 Iniciando aplicação completa..."
USE_MOCK_ICUE=True python3 run.py
```

## 🐛 Troubleshooting Rápido

### Erro: "Music is not running"
```bash
open -a "Music"  # Abra o Apple Music
```

### Erro: "operation not permitted"
```
System Preferences > Security & Privacy > Privacy > Automation
✓ Terminal -> Music.app
```

### Erro: "No module named..."
```bash
pip3 install -r requirements.txt
```

## 💡 Próximos Passos

1. **Ajuste configurações** no `.env`:
   ```env
   UPDATE_INTERVAL=2.0   # Intervalo de verificação
   FADE_DURATION=1.0     # Duração do fade
   ```

2. **Explore a API**:
   - GET `/status` - Status completo
   - GET `/current` - Música atual
   - POST `/config` - Atualizar configurações

3. **Veja os logs**:
   ```bash
   tail -f logs/icue_applemusic.log
   ```

4. **Leia a documentação completa**:
   - [README_MACOS.md](README_MACOS.md) - Guia completo
   - [README.md](README.md) - Documentação principal

## ⚡ One-liner para Demonstração

```bash
open -a "Music" && sleep 2 && USE_MOCK_ICUE=True python3 run.py
```

---

**🎉 Pronto!** Em menos de 5 minutos você está testando o sistema completo!
