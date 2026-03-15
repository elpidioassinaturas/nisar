@echo off
title NISAR Downloader
echo.
echo  =========================================
echo    NISAR Downloader - Interface Web
echo  =========================================
echo.

:: Instala dependencias se necessario
echo  Verificando dependencias...
pip install flask asf_search pyyaml -q

echo.
echo  Iniciando servidor...
echo  A interface abrira automaticamente no navegador.
echo  Para encerrar: feche esta janela ou pressione Ctrl+C
echo.

python app.py
pause
