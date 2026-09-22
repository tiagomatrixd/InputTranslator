@echo off
cd /d "%~dp0"
echo ========================================================
echo   Compilando InputTranslator para Executavel Standalone
echo ========================================================

pyinstaller --noconsole --onefile ^
    --name="InputTranslator" ^
    --icon="assets/icon.ico" ^
    --add-data="assets;assets" ^
    --clean ^
    src/main.py

echo.
if exist "dist\InputTranslator.exe" (
    echo ========================================================
    echo   SUCESSO! O executavel foi gerado em:
    echo   dist\InputTranslator.exe
    echo ========================================================
) else (
    echo Ocorreu um erro durante a compilacao.
)
pause
