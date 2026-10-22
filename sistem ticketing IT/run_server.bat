@echo off
title IT Ticketing Production Server (Waitress)
color 0a

echo ================================================================
echo      MENJALANKAN SERVER TICKETING IT (PRODUCTION MODE)
echo ================================================================
echo.

:: Pastikan dependensi sudah terpasang
python -m pip install -r requirements.txt --quiet

echo [OK] Dependensi terverifikasi.
echo.

:: Menjalankan production server
python server.py

pause
