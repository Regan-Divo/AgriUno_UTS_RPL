"""
==========================================================
MESIN DATABASE BAWAAN - AGRIUNO
==========================================================
Memastikan basis data siap sebelum jendela apa pun tampil.

Alur yang dijamin modul ini:

1. Cek apakah server MySQL sudah berjalan pada ``DB_HOST:DB_PORT``.
   Bila sudah, langkah disingkat: cukup pastikan database ``agriuno``
   beserta isinya tersedia.

2. Bila server belum berjalan, hidupkan salinan mesin MySQL bawaan
   yang ikut didistribusikan pada folder ``runtime/mysql`` sehingga
   pengguna tidak perlu memasang Laragon maupun mengatur apa pun.
   Data tersimpan pada folder ``runtime/data`` di samping aplikasi.

3. Bila database ``agriuno`` belum ada atau masih kosong, berkas
   ``database.sql`` diimpor otomatis sehingga akun demo langsung
   dapat dipakai pada percobaan masuk pertama.

Seluruh kegagalan dikembalikan sebagai pasangan (status, pesan)
tanpa melemparkan galat ke lapisan antarmuka (NFR-03).
"""

import logging
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

#: Batas waktu (detik) menunggu proses inisialisasi folder data.
BATAS_INISIALISASI = 300


# ------------------------------------------------------------
# Lokasi berkas
# ------------------------------------------------------------
def basis_direktori():
    """Folder tempat aplikasi dipasang.

    Untuk aplikasi pemaketan (PyInstaller) folder ini adalah lokasi
    berkas ``.exe``; untuk kode sumber adalah akar repositori.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def cari_mysqld():
    """Mengembalikan lokasi ``mysqld.exe`` bawaan, atau ``None``."""
    kandidat = [
        basis_direktori() / "runtime" / "mysql" / "bin" / "mysqld.exe",
        basis_direktori() / "mysql" / "bin" / "mysqld.exe",
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
    except mysql.connector.Error as exc:
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
    hasil = subprocess.run(
        perintah,
        capture_output=True,
        text=True,
        timeout=BATAS_INISIALISASI,
    )
    if hasil.returncode != 0:
        logger.error("Inisialisasi data MySQL gagal: %s", hasil.stderr[-500:])
        return False
    logger.info("Folder data MySQL bawaan berhasil disiapkan.")
    return True


def _hidupkan_server(mysqld, datadir):
    """Menjalankan ``mysqld`` sebagai proses terpisah (tetap hidup)."""
    log = basis_direktori() / "runtime" / "mysqld.log"
    berkas_log = None
    try:
        berkas_log = open(log, "w", encoding="utf-8")
        subprocess.Popen(
            [
                str(mysqld),
                "--no-defaults",
                "--console",
                "--basedir=%s" % mysqld.parent.parent,
                "--datadir=%s" % datadir,
                "--port=%d" % DB_PORT,
                "--bind-address=127.0.0.1",
            ],
            stdout=berkas_log,
            stderr=berkas_log,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.DETACHED_PROCESS,
            close_fds=True,
        )
        logger.info("Mesin MySQL bawaan dijalankan pada port %d.", DB_PORT)
    finally:
        if berkas_log is not None:
            berkas_log.close()


def _impor_database():
    """Mengimpor ``database.sql`` melalui klien ``mysql.exe`` bawaan."""
    sumber = basis_direktori() / "database.sql"
    klien = cari_mysqld().parent / "mysql.exe"
    if not sumber.is_file() or not klien.is_file():
        logger.error("Berkas database.sql atau klien mysql.exe tidak ditemukan.")
        return False
    with open(sumber, "r", encoding="utf-8") as aliran:
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
        )
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
        # --- Tahap 1: pastikan server hidup -----------------------
        if not server_hidup():
            mysqld = cari_mysqld()
            if mysqld is None:
                return False, (
                    "Mesin data bawaan tidak ditemukan pada folder runtime. "
                    "Nyalakan MySQL (mis. Laragon) lalu buka aplikasi lagi."
                )
            datadir = basis_direktori() / "runtime" / "data"
            if not datadir.exists() and not _inisialisasi_data(mysqld, datadir):
                return False, (
                    "Persiapan data pertama gagal. Jalankan aplikasi sekali "
                    "lagi; bila masih gagal, periksa runtime/mysqld.log."
                )
            _hidupkan_server(mysqld, datadir)
            if not tunggu_server():
                return False, (
                    "Mesin data belum merespons. Tunggu sejenak lalu buka "
                    "aplikasi lagi (periksa runtime/mysqld.log)."
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
