@echo off
echo ============================================
echo   Acumatica ERP Prototipo - USFX SIS-315
echo ============================================
echo.
echo Instalando dependencias...
pip install flask -q
echo.
echo Iniciando servidor Flask en http://localhost:5000
echo Presiona Ctrl+C para detener el servidor.
echo.
python app.py
pause
