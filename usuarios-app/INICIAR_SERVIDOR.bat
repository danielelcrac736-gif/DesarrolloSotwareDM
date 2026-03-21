@echo off
echo.
echo === Iniciando Gestion de Usuarios ===
echo.
echo Cambiando al directorio backend...
cd /d "%~dp0backend"

echo.
echo Iniciando servidor en puerto 3000...
echo.
echo ========================================
echo.
echo 🔐 Credenciales de prueba:
echo    Email: admin@example.com
echo    Clave: 123456
echo.
echo ========================================
echo.
node server.js

pause
