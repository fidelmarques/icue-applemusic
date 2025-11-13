# 🎵 Apple Music to Corsair iCUE LCD

Exiba a capa animada do que você está ouvindo no Apple Music diretamente na tela LCD do seu water cooler Corsair H150i Elite LCD XT!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Características

- 🎨 **Capas Animadas**: Transições suaves com efeito fade in/out
- 🔄 **Atualização Automática**: Detecta mudanças de música em tempo real
- 🌐 **API REST**: Controle e monitore via HTTP
- 💾 **Cache Inteligente**: Evita downloads desnecessários
- 🎯 **Fácil de Usar**: Configure e rode em minutos
- 🔌 **Integração Nativa**: Usa iTunes COM API no Windows

## 📋 Requisitos

### Hardware
- **Corsair H150i Elite LCD XT** (ou outro dispositivo Corsair com LCD de 480x480)
- **Windows 10/11**

### Software
- **Python 3.8+**
- **Apple Music / iTunes** instalado no Windows
- **Corsair iCUE** instalado e rodando
- **iCUE SDK** instalado

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/icue-applemusic.git
cd icue-applemusic
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Instale o iCUE SDK

1. Baixe o [Corsair iCUE SDK](https://github.com/CorsairOfficial/cue-sdk)
2. Instale seguindo as instruções oficiais
3. Certifique-se de que o iCUE está rodando

### 4. Configure o ambiente

```bash
cp .env.example .env
```

Edite o `.env` com suas preferências:

```env
# Configurações do servidor
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Configurações do iCUE
LCD_WIDTH=480
LCD_HEIGHT=480

# Configurações de atualização
UPDATE_INTERVAL=2.0      # Intervalo de verificação (segundos)
FADE_DURATION=1.0        # Duração da animação fade (segundos)
CACHE_DIR=./cache

# Modo de desenvolvimento (usar mock do iCUE)
USE_MOCK_ICUE=False
```

## 🎮 Uso

### Modo Standalone

Execute diretamente para sincronizar as capas:

```bash
python run.py
```

Isso iniciará o monitor que:
1. ✅ Conecta ao Apple Music/iTunes
2. ✅ Monitora a música atual
3. ✅ Baixa e processa capas
4. ✅ Exibe no LCD com animações fade

### Modo API Server

Execute o servidor REST para controle remoto:

```bash
python run_api.py
```

O servidor estará disponível em `http://localhost:5000`

#### Endpoints da API

**GET /** - Informações da API
```bash
curl http://localhost:5000/
```

**GET /status** - Status completo da aplicação
```bash
curl http://localhost:5000/status
```

**GET /current** - Música atual
```bash
curl http://localhost:5000/current
```

**POST /start** - Inicia sincronização
```bash
curl -X POST http://localhost:5000/start
```

**POST /stop** - Para sincronização
```bash
curl -X POST http://localhost:5000/stop
```

**GET /config** - Obter configurações
```bash
curl http://localhost:5000/config
```

**POST /config** - Atualizar configurações
```bash
curl -X POST http://localhost:5000/config \
  -H "Content-Type: application/json" \
  -d '{"update_interval": 3.0, "fade_duration": 1.5}'
```

**GET /health** - Health check
```bash
curl http://localhost:5000/health
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
icue-applemusic/
├── src/
│   ├── __init__.py
│   ├── apple_music_monitor.py  # Monitor do Apple Music
│   ├── image_processor.py      # Processamento de imagens
│   ├── icue_controller.py      # Controle do iCUE SDK
│   ├── main.py                 # Aplicação principal
│   └── api.py                  # Servidor REST API
├── cache/                      # Cache de imagens
├── logs/                       # Arquivos de log
├── .env                        # Configurações
├── requirements.txt            # Dependências Python
├── run.py                      # Script standalone
├── run_api.py                  # Script API server
└── README.md
```

### Testes sem Hardware

Para desenvolver sem o hardware Corsair, use o modo mock:

```bash
# No .env
USE_MOCK_ICUE=True
```

Isso simula o controlador iCUE sem necessitar do hardware real.

### Testando Componentes Individuais

```bash
# Testar monitor do Apple Music
python src/apple_music_monitor.py

# Testar processador de imagens
python src/image_processor.py

# Testar controlador iCUE
python src/icue_controller.py
```

## 🐛 Troubleshooting

### Erro: "pywin32 não está instalado"

```bash
pip install pywin32
python -m win32com.client
```

### Erro: "Não foi possível conectar ao iTunes"

1. Certifique-se de que o iTunes/Apple Music está aberto
2. Toque uma música para ativar a API COM
3. Verifique se o iTunes está atualizado

### Erro: "Falha ao conectar ao iCUE SDK"

1. Certifique-se de que o iCUE está instalado e rodando
2. Verifique se o SDK foi instalado corretamente
3. Reinicie o iCUE
4. Execute como administrador se necessário

### LCD não atualiza

1. Verifique se o dispositivo está conectado corretamente
2. Abra o iCUE e confirme que o LCD está funcionando
3. Verifique os logs em `logs/icue_applemusic.log`
4. Tente aumentar o `UPDATE_INTERVAL` no `.env`

## 🎨 Personalizações

### Alterar Tamanho do LCD

Se seu dispositivo tem um LCD diferente de 480x480, ajuste no `.env`:

```env
LCD_WIDTH=320
LCD_HEIGHT=320
```

### Ajustar Animação

```env
FADE_DURATION=2.0    # Fade mais lento
UPDATE_INTERVAL=1.0  # Verifica mais frequentemente
```

### Cache de Imagens

Por padrão, as capas processadas são salvas em `./cache`. Para mudar:

```env
CACHE_DIR=C:/Users/SeuUsuario/AppData/Local/iCUE-AppleMusic/cache
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- [Corsair](https://www.corsair.com/) pelo iCUE SDK
- [Apple](https://www.apple.com/) pelo Apple Music
- Comunidade Python por bibliotecas incríveis

## 📧 Suporte

Encontrou um bug? Tem uma sugestão?

- Abra uma [issue](https://github.com/seu-usuario/icue-applemusic/issues)
- Entre em contato via [email](mailto:seu-email@example.com)

---

Feito com ❤️ para os amantes de música e hardware!
