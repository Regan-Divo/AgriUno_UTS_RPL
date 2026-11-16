FOLDER runtime
================

Folder ini menjadi tempat mesin MySQL portable (folder mysql/) ketika
aplikasi dibangun menjadi satu berkas .exe. Isinya tidak disertakan
pada paket unggah karena berukuran besar (sekitar 75 MB) dan tidak
perlu untuk menjalankan aplikasi yang sudah dikemas.

Langkah memulihkan (butuh MySQL portable dari Laragon):

  xcopy /E /I "C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin" runtime\mysql\bin
  xcopy /E /I "C:\laragon\bin\mysql\mysql-8.4.3-winx64\share\english" runtime\mysql\share\english
  xcopy /E /I "C:\laragon\bin\mysql\mysql-8.4.3-winx64\share\charsets" runtime\mysql\share\charsets

Setelah itu jalankan:  pyinstaller AgriUno-Studio.spec --noconfirm
