# 📦 Guia de Instalação Detalhado

Este guia fornece instruções passo a passo para instalar e configurar o Apple Music to iCUE LCD no Windows.

## 📋 Pré-requisitos

### 1. Verificar Versão do Python

Abra o PowerShell ou CMD e execute:

```bash
python --version
```

Você deve ter **Python 3.8 ou superior**. Se não tiver, baixe em [python.org](https://www.python.org/downloads/).

**⚠️ IMPORTANTE**: Durante a instalação do Python, marque a opção **"Add Python to PATH"**!

### 2. Instalar Apple Music / iTunes

1. Baixe o [iTunes para Windows](https://www.apple.com/itunes/download/) ou use o Apple Music
2. Instale e configure com sua conta Apple
3. Certifique-se de que está funcionando normalmente

### 3. Instalar Corsair iCUE

1. Baixe o [Corsair iCUE](https://www.corsair.com/icue)
2. Instale a versão mais recente
3. Conecte seu H150i Elite LCD XT
4. Abra o iCUE e confirme que o dispositivo foi detectado

### 4. Instalar iCUE SDK

1. Acesse [CUE SDK no GitHub](https://github.com/CorsairOfficial/cue-sdk-python)
2. Siga as instruções de instalação do SDK
3. Ou instale via pip (se disponível):

```bash
pip install cuesdk
```

**Nota**: O SDK pode requerer componentes adicionais da Corsair. Consulte a documentação oficial.

## 🚀 Instalação do Projeto

### Passo 1: Clonar ou Baixar o Repositório

**Opção A: Com Git**

```bash
git clone https://github.com/seu-usuario/icue-applemusic.git
cd icue-applemusic
```

**Opção B: Download Manual**

1. Baixe o ZIP do repositório
2. Extraia para uma pasta de sua escolha
3. Abra o terminal nessa pasta

### Passo 2: Criar Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar no Windows (CMD)
.\venv\Scripts\activate.bat
```

### Passo 3: Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Editar com seu editor preferido
notepad .env
```

Ajuste as configurações conforme necessário:

```env
# Intervalo de verificação (segundos)
UPDATE_INTERVAL=2.0

# Duração da animação fade (segundos)
FADE_DURATION=1.0

# Diretório de cache
CACHE_DIR=./cache

# Para testes sem hardware
USE_MOCK_ICUE=False
```

## ✅ Verificação da Instalação

### Teste 1: Verificar Dependências

```bash
python -c "import win32com.client; print('✅ pywin32 OK')"
python -c "from PIL import Image; print('✅ Pillow OK')"
python -c "import flask; print('✅ Flask OK')"
```

### Teste 2: Testar Monitor do Apple Music

```bash
python src/apple_music_monitor.py
```

Deve exibir informações da música atual (se estiver tocando).

### Teste 3: Testar iCUE Controller

```bash
python src/icue_controller.py
```

Deve conectar ao iCUE SDK.

### Teste 4: Executar Aplicação

```bash
python run.py
```

Se tudo estiver configurado, você deve ver:

```
2025-01-13 10:00:00 [INFO] ============================================================
2025-01-13 10:00:00 [INFO] Apple Music to iCUE LCD - Iniciando...
2025-01-13 10:00:00 [INFO] ============================================================
2025-01-13 10:00:00 [INFO] ✅ Monitor do Apple Music inicializado
2025-01-13 10:00:00 [INFO] ✅ Processador de imagens inicializado
2025-01-13 10:00:00 [INFO] ✅ iCUE Controller inicializado
2025-01-13 10:00:00 [INFO] 🚀 Aplicação iniciada!
```

## 🐛 Resolução de Problemas

### Erro: "pip não é reconhecido"

Python não está no PATH. Reinstale o Python marcando "Add to PATH" ou adicione manualmente:

1. Pesquise "Variáveis de Ambiente" no Windows
2. Edite a variável PATH
3. Adicione: `C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python3X`

### Erro: "Não foi possível importar win32com"

```bash
pip uninstall pywin32
pip install pywin32
python -m win32com.client
```

Se ainda não funcionar:

```bash
pip install --upgrade pywin32
python Scripts/pywin32_postinstall.py -install
```

### Erro: "ModuleNotFoundError: No module named 'cue_sdk'"

O cue_sdk pode não estar disponível no PyPI. Opções:

1. Instale manualmente seguindo [instruções oficiais](https://github.com/CorsairOfficial/cue-sdk-python)
2. Use modo mock para desenvolvimento: `USE_MOCK_ICUE=True` no `.env`

### Erro: "Permissão negada"

Execute o terminal como **Administrador** no Windows.

### iCUE não conecta

1. Feche e reabra o iCUE
2. Certifique-se de que o dispositivo está conectado e detectado
3. Verifique se outros programas não estão usando o SDK
4. Reinicie o computador

## 🎯 Próximos Passos

Após a instalação bem-sucedida:

1. **Execute o servidor API** (opcional):
   ```bash
   python run_api.py
   ```

2. **Acesse a interface web** (se disponível):
   ```
   http://localhost:5000
   ```

3. **Configure para iniciar automaticamente** (opcional):
   - Crie um atalho no Windows
   - Adicione à pasta de inicialização
   - Ou use o Agendador de Tarefas

## 📚 Recursos Adicionais

- [Documentação do iCUE SDK](https://github.com/CorsairOfficial/cue-sdk)
- [Documentação do pywin32](https://github.com/mhammond/pywin32)
- [Pillow (PIL) Documentation](https://pillow.readthedocs.io/)

## 💬 Precisa de Ajuda?

Se você seguiu todos os passos e ainda tem problemas:

1. Verifique os logs em `logs/icue_applemusic.log`
2. Abra uma [issue no GitHub](https://github.com/seu-usuario/icue-applemusic/issues)
3. Inclua:
   - Versão do Python
   - Versão do Windows
   - Mensagem de erro completa
   - Conteúdo do log

---

Boa sorte! 🎵🎨
