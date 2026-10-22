@echo off
title IT Helpdesk & Ticketing System
color 0b
echo ================================================================
echo           SISTEM TICKETING IT & MONITORING DEPARTEMEN
echo ================================================================
echo.
echo Sedang menyiapkan sistem...
echo.

:: Pastikan dependensi terinstall
python -m pip install -r requirements.txt --quiet

echo.
echo [OK] Sistem siap dijalankan!
echo.
echo ================================================================
echo  ALAMAT AKSES SISTEM:
echo.
echo  1. Akses dari Komputer Ini (IT):
echo     http://localhost:5000/it/dashboard
echo.
echo  2. Akses dari Departemen Lain (Jaringan Kantor / LAN):
echo     http://161.60.11.15:5000
echo.
echo ================================================================
echo Tekan CTRL + C di jendela ini untuk mematikan server.
echo.

python app.py

pause
