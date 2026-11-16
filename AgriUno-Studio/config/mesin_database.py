"""
==========================================================
MESIN DATABASE BAWAAN - AGRIUNO EDISI STUDIO
==========================================================
Memastikan basis data siap sebelum jendela apa pun tampil.

Alur yang dijamin modul ini:

1. Cek apakah server MySQL sudah berjalan pada ``DB_HOST:DB_PORT``.
   Bila sudah, langkah disingkat: cukup pastikan database ``agriuno``
   beserta isinya tersedia.

2. Bila server belum berjalan, hidupkan salinan mesin MySQL bawaan
   yang ikut dipaketkan di dalam berkas eksekusi sehingga pengguna
   tidak perlu memasang Laragon maupun mengatur apa pun. Mesin
   pertama kali disalin ke folder data aplikasi (%LOCALAPPDATA%),
   lalu dijalankan dari sana dengan data tersimpan pada folder
   ``data`` di sampingnya.

3. Bila database ``agriuno`` belum ada atau masih kosong, berkas
   ``database.sql`` (ikut dipaketkan) diimpor otomatis sehingga akun
   demo langsung dapat dipakai pada percobaan masuk pertama.

Seluruh kegagalan dikembalikan sebagai pasangan (status, pesan)
tanpa melemparkan galat ke lapisan antarmuka (NFR-03).
"""

import logging
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import mysql.connector

from config.database import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

logger = logging.getLogger(__name__)

#: Batas waktu (detik) menunggu server bawaan siap menerima koneksi.
BATAS_MENUNGGU_SERVER = 90

#: Batas waktu (detik) menunggu proses inisialisasi/salin mesin.
BATAS_INISIALISASI = 300


# ------------------------------------------------------------
# Lokasi sumber daya dan data
# ------------------------------------------------------------
def folder_bundel():
    """Folder berisi sumber daya yang ikut dipaketkan.

    Untuk aplikasi pemaketan (PyInstaller onefile) sumber daya
    diekstrak ke folder sementara ``sys._MEIPASS``; untuk kode
    sumber adalah akar repositori.
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def folder_data():
    """Folder data pengguna yang pasti dapat ditulis.

    Aplikasi pemaketan memakai ``%LOCALAPPDATA%\\AgriUnoStudio``
    agar data tetap tersimpan antar sesi; kode sumber memakai akar
    repositori.
    """
    if getattr(sys, "frozen", False):
        dasar = Path(
            os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        ) / "AgriUnoStudio"
    else:
        dasar = Path(__file__).resolve().parent.parent
    dasar.mkdir(parents=True, exist_ok=True)
    return dasar


def _salin_mesin(tujuan):
    """Menyalin mesin MySQL bawaan dari paket ke folder data aplikasi.

    Menyalin (bukan menjalankan langsung dari folder sementara)
    agar berkas mesin tidak terkunci pada folder ekstraksi sementara
    yang dihapus setiap aplikasi ditutup.
    """
    sumber = folder_bundel() / "mysql"
    if not sumber.is_dir():
        logger.error("Folder mesin MySQL tidak ada di dalam paket.")
        return False
    if (tujuan / "bin" / "mysqld.exe").is_file():
        return True
    logger.info("Menyalin mesin data bawaan ke folder aplikasi...")
    shutil.copytree(sumber, tujuan, dirs_exist_ok=True)
    return (tujuan / "bin" / "mysqld.exe").is_file()


def cari_mysqld():
    """Mengembalikan lokasi ``mysqld.exe`` bawaan, atau ``None``."""
    kandidat = [
        folder_data() / "mysql" / "bin" / "mysqld.exe",
        folder_bundel() / "mysql" / "bin" / "mysqld.exe",
        folder_bundel() / "runtime" / "mysql" / "bin" / "mysqld.exe",
    ]
    for berkas in kandidat:
        if berkas.is_file():
            return berkas
    return None


# ------------------------------------------------------------
# Pemeriksaan server dan isi database
# ------------------------------------------------------------
def server_hidup():
    """Benar bila MySQL dapat dihubungi tanpa memilih database."""
    try:
        koneksi = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connection_timeout=3,
        )
        koneksi.close()
        return True
    except Exception as exc:  # noqa: BLE001 - galat apa pun berarti server belum siap
        logger.info("Server MySQL belum dapat dihubungi: %s", exc)
        return False


def database_terisi(koneksi):
    """Benar bila database ``agriuno`` sudah memuat tabel ``users``."""
    try:
        kursor = koneksi.cursor()
        kursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = 'users'",
            (DB_NAME,),
        )
        return kursor.fetchone()[0] > 0
    except mysql.connector.Error:
        return False


def tunggu_server(batas_detik=BATAS_MENUNGGU_SERVER):
    """Menunggu port MySQL terbuka hingga batas waktu."""
    tenggat = time.time() + batas_detik
    while time.time() < tenggat:
        try:
            with socket.create_connection((DB_HOST, DB_PORT), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    return False


# ------------------------------------------------------------
# Menjalankan mesin bawaan
# ------------------------------------------------------------
def _inisialisasi_data(mysqld, datadir):
    """Menyiapkan folder data baru (sekali, pada pemakaian pertama)."""
    perintah = [
        str(mysqld),
        "--no-defaults",
        "--initialize-insecure",
        "--basedir=%s" % mysqld.parent.parent,
        "--datadir=%s" % datadir,
    ]
    try:
        hasil = subprocess.run(
            perintah,
            capture_output=True,
            text=True,
            timeout=BATAS_INISIALISASI,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except subprocess.TimeoutExpired:
        logger.error("Inisialisasi data MySQL melebihi batas waktu.")
        return False
    if hasil.returncode != 0:
        logger.error("Inisialisasi data MySQL gagal: %s", hasil.stderr[-500:])
        return False
    logger.info("Folder data MySQL bawaan berhasil disiapkan.")
    return True


def _hidupkan_server(mysqld, datadir):
    """Menjalankan ``mysqld`` sebagai proses terpisah (tetap hidup).

    Log galat diarahkan ke berkas ``mysqld.log`` lewat ``--log-error``
    (tanpa ``--console``) agar mysqld tidak membuat jendela konsol
    pada komputer pengguna.
    """
    log = folder_data() / "mysqld.log"
    try:
        subprocess.Popen(
            [
                str(mysqld),
                "--no-defaults",
                "--basedir=%s" % mysqld.parent.parent,
                "--datadir=%s" % datadir,
                "--log-error=%s" % log,
                "--port=%d" % DB_PORT,
                "--bind-address=127.0.0.1",
            ],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NO_WINDOW,
            close_fds=True,
        )
        logger.info("Mesin MySQL bawaan dijalankan pada port %d.", DB_PORT)
    except OSError as exc:
        logger.error("Gagal menjalankan mesin MySQL bawaan: %s", exc)


def _impor_database():
    """Mengimpor ``database.sql`` melalui klien ``mysql.exe`` bawaan."""
    sumber = folder_bundel() / "database.sql"
    if not sumber.is_file():
        sumber = folder_bundel().parent / "database.sql"
    mysqld = cari_mysqld()
    klien = mysqld.parent / "mysql.exe" if mysqld else None
    if not sumber.is_file() or klien is None or not klien.is_file():
        logger.error("Berkas database.sql atau klien mysql.exe tidak ditemukan.")
        return False
    with open(sumber, "r", encoding="utf-8") as aliran:
        try:
            hasil = subprocess.run(
                [
                    str(klien),
                    "--no-defaults",
                    "--host=%s" % DB_HOST,
                    "--port=%d" % DB_PORT,
                    "--user=%s" % DB_USER,
                ],
                stdin=aliran,
                capture_output=True,
                text=True,
                timeout=BATAS_INISIALISASI,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except subprocess.TimeoutExpired:
            logger.error("Impor database.sql melebihi batas waktu.")
            return False
    if hasil.returncode != 0:
        logger.error("Impor database.sql gagal: %s", hasil.stderr[-500:])
        return False
    logger.info("Database %s berhasil diimpor dari database.sql.", DB_NAME)
    return True


# ------------------------------------------------------------
# Titik masuk utama
# ------------------------------------------------------------
def siapkan_database():
    """Memastikan server MySQL hidup dan database ``agriuno`` terisi.

    Mengembalikan pasangan ``(berhasil, pesan)``. Fungsi ini tidak
    pernah melemparkan galat, sehingga pemanggil (main.py) tetap
    aman dilanjutkan ke jendela aplikasi.
    """
    try:
        logger.info(
            "Mulai: frozen=%s, bundel=%s, target_host=%s:%s",
            getattr(sys, "frozen", False), folder_bundel(), DB_HOST, DB_PORT,
        )
        # --- Tahap 1: pastikan server hidup -----------------------
        if not server_hidup():
            if getattr(sys, "frozen", False):
                # Mesin disalin ke folder data agar tidak berjalan dari
                # folder ekstraksi sementara yang dihapus tiap ditutup.
                tujuan_mesin = folder_data() / "mysql"
                logger.info("Menyalin mesin ke %s", tujuan_mesin)
                if not _salin_mesin(tujuan_mesin):
                    return False, (
                        "Mesin data bawaan tidak ditemukan. Jalankan aplikasi "
                        "sekali lagi; bila masih gagal, pasang MySQL (mis. "
                        "Laragon) lalu buka aplikasi."
                    )
            mysqld = cari_mysqld()
            logger.info("mysqld: %s", mysqld)
            if mysqld is None:
                return False, (
                    "Mesin data bawaan tidak ditemukan. Jalankan aplikasi "
                    "sekali lagi; bila masih gagal, pasang MySQL (mis. "
                    "Laragon) lalu buka aplikasi."
                )
            datadir = folder_data() / "data"
            if not datadir.exists() and not _inisialisasi_data(mysqld, datadir):
                return False, (
                    "Persiapan data pertama gagal. Jalankan aplikasi sekali "
                    "lagi; bila masih gagal, periksa mysqld.log pada folder "
                    "data aplikasi."
                )
            _hidupkan_server(mysqld, datadir)
            if not tunggu_server():
                return False, (
                    "Mesin data belum merespons. Tunggu sejenak lalu buka "
                    "aplikasi lagi (periksa mysqld.log pada folder data "
                    "aplikasi)."
                )
            logger.info("Server MySQL bawaan siap.")

        # --- Tahap 2: pastikan database terisi --------------------
        koneksi = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connection_timeout=5,
        )
        try:
            if not database_terisi(koneksi):
                if not _impor_database():
                    return False, (
                        "Basis data %s belum dapat diisi otomatis. Impor "
                        "database.sql secara manual (lihat BACA-SAYA)." % DB_NAME
                    )
        finally:
            koneksi.close()
        return True, ""
    except Exception as exc:  # noqa: BLE001 - jaring pengaman terakhir
        logger.error("Persiapan database gagal: %s", exc)
        return False, "Persiapan database gagal: %s" % exc
