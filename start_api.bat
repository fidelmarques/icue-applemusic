@echo off
REM Script para iniciar o servidor API no Windows

echo ========================================
echo  Apple Music to iCUE LCD - API Server
echo ========================================
echo.

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8+ de https://www.python.org
    pause
    exit /b 1
)

REM Ativa ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Verifica dependências
echo Verificando dependencias...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Dependencias nao encontradas. Instalando...
    pip install -r requirements.txt
)

REM Executa o servidor API
echo.
echo Iniciando servidor API...
echo Servidor disponivel em: http://localhost:5000
echo Pressione Ctrl+C para parar
echo.

python run_api.py

pause
