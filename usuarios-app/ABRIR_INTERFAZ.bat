@echo off
echo.
echo === Abrir Interfaz Grafica ===
echo.
echo Abriendo index.html en el navegador...
echo.
timeout /t 2 /nobreak

cd /d "%~dp0frontend"
start "" "index.html"

echo.
echo Interfaz abierta en tu navegador por defecto.
echo.
pause
