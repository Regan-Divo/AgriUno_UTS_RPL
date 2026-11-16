@echo off
REM ============================================================
REM  PELUNCUR APLIKASI AGRIUNO
REM ============================================================
REM  Berkas ini dapat diklik dua kali (double-click) untuk membuka
REM  aplikasi AgriUno.
REM
REM  Aplikasi desktop, BUKAN aplikasi web. Tidak memerlukan
REM  Laravel, XAMPP, maupun browser.
REM
REM  Prasyarat: layanan MySQL pada Laragon harus sedang aktif.
REM ============================================================

setlocal
cd /d "%~dp0"
title AgriUno - Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal

echo.
echo   ==================================================
echo      AGRIUNO - Aplikasi Desktop Manajemen Gudang
echo   ==================================================
echo.

REM --- Periksa layanan MySQL ---
netstat -ano | findstr ":3306" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   [PERINGATAN] Layanan MySQL tidak terdeteksi.
    echo.
    echo   Buka Laragon lalu klik "Start All", kemudian jalankan
    echo   berkas ini kembali.
    echo.
    pause
    exit /b 1
)
echo   [OK] MySQL aktif di port 3306.

REM --- Jalankan berkas .exe bila tersedia ---
if exist "dist\AgriUno.exe" (
    echo   [OK] Menjalankan AgriUno.exe
    echo.
    start "" "dist\AgriUno.exe"
    goto :selesai
)

REM --- Jika .exe belum tersedia, jalankan dengan Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo   [PERINGATAN] Python tidak ditemukan di PATH dan berkas
    echo   AgriUno.exe belum dibangun.
    echo.
    echo   Untuk membangun berkas .exe, jalankan perintah berikut
    echo   pada terminal di folder proyek ini:
    echo.
    echo       pip install pyinstaller
    echo       pyinstaller --noconfirm --clean AgriUno.spec
    echo.
    pause
    exit /b 1
)

echo   [OK] Menjalankan dengan Python
echo.
python main.py

:selesai
endlocal
