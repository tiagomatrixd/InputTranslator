@echo off
cd /d "%~dp0"

if "%1"=="--debug" (
    echo Iniciando InputTranslator em modo depuracao (console ativo)...
    python src\main.py
) else (
    echo Iniciando InputTranslator em segundo plano...
    start "" pythonw src\main.py
)
