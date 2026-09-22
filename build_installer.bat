@echo off
cd /d "%~dp0"
echo ========================================================
echo   Compilando Instalador Oficial do InputTranslator
echo ========================================================

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo Erro: Inno Setup 6 nao encontrado em Arquivos de Programas.
    pause
    exit /b 1
)

"%ISCC%" installer.iss

echo.
if exist "InputTranslator-Setup.exe" (
    echo ========================================================
    echo   SUCESSO! O Instalador foi gerado com sucesso:
    echo   d:\Tiago\WINMERGE\InputTranslator-Setup.exe
    echo ========================================================
) else (
    echo Ocorreu um erro na geracao do instalador.
)
pause
