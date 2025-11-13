# 🍎 Testando no macOS

Este guia mostra como testar o projeto no macOS sem o hardware Corsair.

## ✅ O que funciona no macOS

- ✅ Monitor do Apple Music via AppleScript (nativo)
- ✅ Processamento de imagens com fade
- ✅ Modo Mock do iCUE (simulação)
- ✅ API REST completa
- ✅ Todos os testes e desenvolvimento

## ⚠️ O que NÃO funciona no macOS

- ❌ iCUE SDK (Corsair iCUE não está disponível para macOS)
- ❌ Exibição real no LCD (requer Windows + hardware)

## 🚀 Instalação Rápida no macOS

### 1. Pré-requisitos

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python 3
brew install python3
```

### 2. Clonar e instalar

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/icue-applemusic.git
cd icue-applemusic

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações (opcional)
nano .env
```

No `.env`, certifique-se de que:
```env
USE_MOCK_ICUE=True  # Obrigatório no macOS
```

## 🧪 Testes

### Teste 1: Monitor do Apple Music

```bash
# Toque uma música no Apple Music primeiro!
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

### Teste 2: Aplicação Completa (Modo Mock)

```bash
# Executa com mock do iCUE
./run_macos.sh
```

Saída esperada:
```
========================================
 Apple Music to iCUE LCD - macOS
========================================

✅ Python 3.11.x encontrado
✅ Monitor do Apple Music inicializado (macOS)
✅ Processador de imagens inicializado
✅ Mock iCUE Controller inicializado

🚀 Aplicação iniciada!
   Intervalo de atualização: 2.0s
   Duração do fade: 1.0s
```

### Teste 3: API Server

```bash
# Terminal 1: Inicia o servidor
python3 run_api.py

# Terminal 2: Testa os endpoints
curl http://localhost:5000/status
curl http://localhost:5000/current
```

## 🎨 Verificar Processamento de Imagens

As capas processadas ficam em `./cache/`. Você pode abrir para ver:

```bash
# Ver última capa processada
open cache/*.png

# Ou listar todas
ls -lht cache/
```

## 🔧 Desenvolvimento no macOS

### Estrutura de Testes

```bash
icue-applemusic/
├── test_macos.sh          # Teste do monitor AppleScript
├── run_macos.sh           # Executa aplicação em modo mock
└── src/
    ├── apple_music_monitor_macos.py  # Monitor para macOS
    └── ...
```

### Testando Componentes Individualmente

```bash
# Monitor do Apple Music (AppleScript)
python3 src/apple_music_monitor_macos.py

# Processador de imagens
python3 src/image_processor.py

# Mock iCUE Controller
python3 src/icue_controller.py
```

### Debug e Logs

```bash
# Ver logs em tempo real
tail -f logs/icue_applemusic.log

# Ver últimas 50 linhas
tail -50 logs/icue_applemusic.log
```

## 📸 Exemplo de Uso

1. **Abra o Apple Music** e toque uma música
2. **Execute o script**:
   ```bash
   ./run_macos.sh
   ```
3. **Observe os logs**:
   ```
   2025-01-13 10:00:00 [INFO] 🎵 Nova música detectada: Artist - Song
   2025-01-13 10:00:01 [INFO] 🖼️  Atualizando display com fade...
   2025-01-13 10:00:02 [INFO] Mock: Fade transition (1.0s @ 30fps)
   ```
4. **Verifique a capa processada** em `cache/`

## 🐛 Troubleshooting macOS

### Erro: "operation not permitted" ao executar AppleScript

```bash
# Dar permissão ao Terminal para controlar o Music
# Vá em: System Preferences > Security & Privacy > Privacy > Automation
# Marque: Terminal -> Music.app
```

### Erro: "Music is not running"

```bash
# Abrir Apple Music manualmente
open -a "Music"

# Ou deixar o script abrir automaticamente
```

### Erro: "No module named 'win32com'"

Isso é normal no macOS! O código detecta automaticamente o SO e usa AppleScript em vez de pywin32.

### AppleScript muito lento

Se o AppleScript estiver demorando muito:

1. Certifique-se de que o Apple Music está aberto
2. Toque uma música antes de iniciar o script
3. Reduza `UPDATE_INTERVAL` no `.env` se necessário

## 🎯 Limitações no macOS

Como o iCUE não existe para macOS, você **não pode** exibir no LCD real. Mas você **pode**:

- ✅ Desenvolver toda a lógica
- ✅ Testar processamento de imagens
- ✅ Testar animações (via mock)
- ✅ Desenvolver a API
- ✅ Testar integração com Apple Music

## 🔄 Workflow Recomendado

1. **Desenvolva no macOS** (mais fácil para Apple Music)
2. **Teste no Windows** com o hardware real
3. **Deploy no Windows** para uso diário

## 💡 Dicas

### Ver AppleScript gerado

O monitor gera scripts AppleScript dinamicamente. Para debug:

```bash
# Edite apple_music_monitor_macos.py
# Adicione print(script) antes de _run_applescript()
```

### Testar AppleScript manualmente

```bash
# Obter música atual
osascript -e 'tell application "Music" to return name of current track'

# Verificar se está tocando
osascript -e 'tell application "Music" to return player state as string'
```

### Melhorar Performance

No `.env`:
```env
UPDATE_INTERVAL=3.0  # Aumentar para menos chamadas ao AppleScript
FADE_DURATION=0.5    # Reduzir para animações mais rápidas
```

## 📚 Recursos Adicionais

- [AppleScript Language Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)
- [Music.app AppleScript Dictionary](https://developer.apple.com/library/archive/documentation/AppleScript/Reference/MusicAppRef/Music.html)

## 🎵 Exemplo Completo

```bash
# Setup inicial (uma vez)
git clone https://github.com/seu-usuario/icue-applemusic.git
cd icue-applemusic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Toda vez que for testar
source venv/bin/activate
open -a "Music"  # Toque uma música!
./test_macos.sh  # Teste rápido
# OU
./run_macos.sh   # Aplicação completa
```

---

**🎉 Pronto!** Agora você pode desenvolver e testar tudo no macOS, e só precisa do Windows para exibir no LCD real!
