# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-01-13

### Adicionado
- 🎵 Monitor do Apple Music via iTunes COM API
- 🎨 Processador de imagens com suporte a redimensionamento e crop
- ✨ Animações fade in/out para transições suaves entre capas
- 🔌 Integração com Corsair iCUE SDK para controle do LCD
- 🌐 API REST completa para controle e monitoramento
- 💾 Sistema de cache para otimizar downloads
- 📝 Logging detalhado com rotação de arquivos
- 🎯 Scripts de inicialização para Windows (.bat)
- 🐛 Modo mock para desenvolvimento sem hardware
- 📚 Documentação completa (README, INSTALL, CHANGELOG)
- ⚙️ Configuração via variáveis de ambiente (.env)

### Características Principais
- Detecção automática de mudança de música
- Suporte a LCD 480x480 (H150i Elite LCD XT)
- Intervalo de atualização configurável
- Duração de fade configurável
- Placeholder quando não há capa disponível
- Endpoints REST para controle remoto
- Health check para monitoramento

### Componentes
- `apple_music_monitor.py`: Monitor do Apple Music
- `image_processor.py`: Processamento de imagens
- `icue_controller.py`: Controle do iCUE SDK
- `main.py`: Aplicação standalone
- `api.py`: Servidor REST API

### Dependências
- Flask 3.0.0
- Pillow 10.1.0
- requests 2.31.0
- pywin32 306
- cuesdk 1.0.0
- python-dotenv 1.0.0
- watchdog 3.0.0

---

## [Unreleased]

### Planejado
- [ ] Interface web para configuração
- [ ] Suporte a Spotify
- [ ] Suporte a outros dispositivos Corsair
- [ ] Overlay com informações da música
- [ ] Visualizador de espectro de áudio
- [ ] Temas personalizáveis
- [ ] Integração com Last.fm para scrobbling
- [ ] Notificações do sistema
- [ ] Sincronização com RGB do sistema
- [ ] Suporte a macOS e Linux

### Em Consideração
- [ ] Equalizer visual
- [ ] Controles de música via API
- [ ] Integração com Discord Rich Presence
- [ ] Suporte a múltiplos monitores/displays
- [ ] Plugin para outros players de música
