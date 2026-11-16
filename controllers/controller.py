"""
==========================================================
CONTROLLER UTAMA - AGRIUNO  (Modul 6: Integrasi Controller)
==========================================================
Jembatan antara antarmuka pengguna (View) dan basis data (Model).

Tanggung jawab:
1. Validasi masukan yang berasal dari form antarmuka.
2. Penerapan aturan bisnis BR-01 sampai BR-11.
3. Orkestrasi pemanggilan kelas model.
4. Pengembalian pasangan ``(berhasil, pesan)`` yang langsung
   dipakai oleh View untuk menampilkan kotak dialog.

Seluruh method bersifat statis karena kelas ini tidak menyimpan
state; state sesi pengguna disimpan pada objek ``Session`` di
berkas ``controllers/auth_controller.py``.
"""

import logging
from datetime import datetime
from decimal import Decimal

from config.constants import (
    STATUS_DIPROSES,
    STATUS_PENGIRIMAN,
    STATUS_TERKIRIM,
)
from controllers.auth_controller import AuthController
from models.distribusi_model import DistribusiModel
from models.panen_model import PanenModel
from models.petani_model import PetaniModel

logger = logging.getLogger(__name__)

#: Format tanggal yang dipakai seluruh form.
FORMAT_TANGGAL = "%Y-%m-%d"


class AgriUnoController:
    """Kontroler utama aplikasi AgriUno."""

    # ========================================================
    # PETANI  (BR-01, BR-03, BR-11)
    # ========================================================
    @staticmethod
    def get_petani():
        """Mengambil seluruh data petani."""
        return PetaniModel.get_all()

    @staticmethod
    def get_petani_by_id(id_petani):
        """Mengambil satu data petani."""
        return PetaniModel.get_by_id(id_petani)

    @staticmethod
    def _norm_teks(teks):
        """Menormalkan teks isian sesuai BR-11.

        Spasi berlebih dirapatkan menjadi satu dan penulisan diubah
        menjadi kapitalisasi gaya judul sehingga ``"JERUK"``,
        ``"jeruk"``, dan ``"Jeruk"`` dianggap nilai yang sama.
        """
        return " ".join(str(teks or "").split()).title()

    @staticmethod
    def _petani_duplikat(nama, lokasi, komoditas, kecuali_id=None):
        """Mencari petani lain dengan identitas identik (BR-11).

        Perbandingan bersifat tidak peka huruf besar-kecil. Bila basis
        data tidak dapat dihubungi, pemeriksaan dilewati (mengembalikan
        None) karena penyimpanan itu sendiri akan gagal kemudian.
        """
        try:
            daftar = PetaniModel.get_all()
        except Exception:  # noqa: BLE001 - server basis data tidak aktif
            logger.warning("Pemeriksaan duplikat dilewati: basis data tidak tersedia.")
            return None

        kunci = (nama.casefold(), lokasi.casefold(), komoditas.casefold())
        for item in daftar:
            if kecuali_id is not None and item["id_petani"] == kecuali_id:
                continue
            milik = (
                str(item["nama_petani"]).casefold(),
                str(item["lokasi_lahan"]).casefold(),
                str(item["komoditas_utama"]).casefold(),
            )
            if milik == kunci:
                return item
        return None

    @staticmethod
    def tambah_petani(nama, lokasi, komoditas):
        """Menambah data petani baru.

        Aturan yang ditegakkan:
        * Ketiga kolom wajib diisi.
        * Panjang teks dibatasi sesuai panjang kolom pada basis data.
        * BR-11: kombinasi nama, lokasi lahan, dan komoditas utama wajib
          unik; teks dinormalkan lebih dahulu agar ``"JERUK"`` dan
          ``"Jeruk"`` tidak dihitung dua data berbeda.
        """
        nama = AgriUnoController._norm_teks(nama)
        lokasi = AgriUnoController._norm_teks(lokasi)
        komoditas = AgriUnoController._norm_teks(komoditas)

        if not nama or not lokasi or not komoditas:
            return False, "Nama, lokasi lahan, dan komoditas utama wajib diisi!"
        if len(nama) > 100:
            return False, "Nama petani maksimal 100 karakter!"
        if len(lokasi) > 150:
            return False, "Lokasi lahan maksimal 150 karakter!"
        if len(komoditas) > 100:
            return False, "Komoditas utama maksimal 100 karakter!"

        duplikat = AgriUnoController._petani_duplikat(nama, lokasi, komoditas)
        if duplikat:
            return False, (
                "Gagal menyimpan! Petani dengan nama, lokasi lahan, dan "
                "komoditas yang sama sudah terdaftar (ID %s - %s) sesuai "
                "aturan BR-11." % (duplikat["id_petani"], duplikat["nama_petani"])
            )

        if not PetaniModel.insert(nama, lokasi, komoditas):
            return False, "Gagal menyimpan data petani ke basis data!"
        return True, "Data petani berhasil disimpan!"

    @staticmethod
    def update_petani(id_petani, nama, lokasi, komoditas):
        """Memperbarui data petani yang sudah ada.

        BR-11 juga ditegakkan di sini: data sendiri dikecualikan dari
        pemeriksaan duplikat sehingga penyimpanan tanpa perubahan tetap
        diperbolehkan.
        """
        if not id_petani:
            return False, "Pilih data petani yang ingin diubah!"

        nama = AgriUnoController._norm_teks(nama)
        lokasi = AgriUnoController._norm_teks(lokasi)
        komoditas = AgriUnoController._norm_teks(komoditas)

        if not nama or not lokasi or not komoditas:
            return False, "Nama, lokasi lahan, dan komoditas utama wajib diisi!"
        if not PetaniModel.exists(id_petani):
            return False, "Data petani tidak ditemukan!"
        if len(nama) > 100:
            return False, "Nama petani maksimal 100 karakter!"
        if len(lokasi) > 150:
            return False, "Lokasi lahan maksimal 150 karakter!"
        if len(komoditas) > 100:
            return False, "Komoditas utama maksimal 100 karakter!"

        duplikat = AgriUnoController._petani_duplikat(nama, lokasi, komoditas, kecuali_id=id_petani)
        if duplikat:
            return False, (
                "Gagal memperbarui! Petani dengan nama, lokasi lahan, dan "
                "komoditas yang sama sudah terdaftar (ID %s - %s) sesuai "
                "aturan BR-11." % (duplikat["id_petani"], duplikat["nama_petani"])
            )

        if not PetaniModel.update(id_petani, nama, lokasi, komoditas):
            return False, "Gagal memperbarui data petani!"
        return True, "Data petani berhasil diperbarui!"

    @staticmethod
    def hapus_petani(id_petani):
        """Menghapus data petani (ditolak bila masih terikat relasi).

        Hak penghapusan data dibatasi untuk peran Administrator saja
        sesuai matriks RBAC.
        """
        if not id_petani:
            return False, "Pilih data petani yang ingin dihapus!"
        if not AuthController.boleh("bisa_hapus_data"):
            return False, (
                "Penghapusan data hanya dapat dilakukan oleh Administrator!"
            )
        return PetaniModel.delete(id_petani)

    # ========================================================
    # PANEN  (BR-01, BR-02)
    # ========================================================
    @staticmethod
    def get_panen():
        """Mengambil seluruh lot panen beserta sisa stoknya."""
        return PanenModel.get_all()

    @staticmethod
    def tambah_panen(id_petani, jenis, berat, tanggal):
        """Mencatat lot setoran panen baru.

        Aturan yang ditegakkan:
        * Semua kolom wajib diisi.
        * Berat harus berupa angka dan lebih besar dari nol.
        * Tanggal harus berformat YYYY-MM-DD dan tidak berada di masa depan.
        * Jenis komoditas dinormalkan sesuai BR-11 (spasi rapat dan
          kapitalisasi judul) agar konsisten dengan master data petani.
        * id_petani wajib menunjuk data petani yang tercatat (BR-01).
        """
        if not id_petani or not jenis or not berat or not tanggal:
            return False, "Seluruh kolom setoran panen wajib diisi!"

        jenis = AgriUnoController._norm_teks(jenis)
        if len(jenis) > 100:
            return False, "Jenis komoditas maksimal 100 karakter!"

        try:
            b_float = float(berat)
        except (TypeError, ValueError):
            return False, "Jumlah berat harus berupa angka numerik!"
        if b_float <= 0:
            return False, "Jumlah berat panen harus berupa angka positif!"

        tanggal = AgriUnoController._validasi_tanggal(tanggal)
        if tanggal is None:
            return False, "Tanggal panen harus berformat YYYY-MM-DD!"

        # BR-01: penyetor wajib terdaftar
        if not PetaniModel.exists(id_petani):
            return False, "ID Petani tidak terdaftar di sistem!"

        if not PanenModel.insert(id_petani, jenis, b_float, tanggal):
            return False, "Gagal menyimpan data panen ke basis data!"
        return True, "Setoran panen berhasil dicatat!"

    @staticmethod
    def update_panen(id_panen, id_petani, jenis, berat, tanggal):
        """Memperbarui lot panen.

        Aturan tambahan: berat baru tidak boleh lebih kecil daripada
        total berat yang sudah dialokasikan ke distributor (BR-02),
        karena hal tersebut akan menghasilkan stok minus.
        """
        if not id_panen:
            return False, "Pilih data panen yang ingin diubah!"
        if not id_petani or not jenis or not berat or not tanggal:
            return False, "Seluruh kolom setoran panen wajib diisi!"

        jenis = AgriUnoController._norm_teks(jenis)
        if len(jenis) > 100:
            return False, "Jenis komoditas maksimal 100 karakter!"

        try:
            b_float = float(berat)
        except (TypeError, ValueError):
            return False, "Jumlah berat harus berupa angka numerik!"
        if b_float <= 0:
            return False, "Jumlah berat panen harus berupa angka positif!"

        tanggal = AgriUnoController._validasi_tanggal(tanggal)
        if tanggal is None:
            return False, "Tanggal panen harus berformat YYYY-MM-DD!"

        if not PetaniModel.exists(id_petani):
            return False, "ID Petani tidak terdaftar di sistem!"

        lot_lama = PanenModel.get_by_id(id_panen)
        if not lot_lama:
            return False, "Data lot panen tidak ditemukan!"

        # BR-02: berat baru minimal sebesar berat yang sudah dialokasikan
        sudah_dialokasikan = PanenModel.get_total_terkirim(id_panen)
        if Decimal(str(b_float)) < sudah_dialokasikan:
            return (
                False,
                "Berat baru (%s Kg) lebih kecil daripada total yang sudah "
                "dialokasikan (%s Kg). Ubah alokasi distribusi terlebih dahulu."
                % (f"{b_float:.2f}", f"{sudah_dialokasikan:.2f}"),
            )

        if not PanenModel.update(id_panen, id_petani, jenis, b_float, tanggal):
            return False, "Gagal memperbarui data panen!"
        return True, "Data panen berhasil diperbarui!"

    @staticmethod
    def hapus_panen(id_panen):
        """Menghapus lot panen (ditolak bila masih terikat alokasi).

        Hak penghapusan data dibatasi untuk peran Administrator saja.
        """
        if not id_panen:
            return False, "Pilih data panen yang ingin dihapus!"
        if not AuthController.boleh("bisa_hapus_data"):
            return False, (
                "Penghapusan data hanya dapat dilakukan oleh Administrator!"
            )
        return PanenModel.delete(id_panen)

    # ========================================================
    # DISTRIBUSI  (BR-02, BR-03, BR-04, BR-05, BR-09)
    # ========================================================
    @staticmethod
    def get_distribusi():
        """Mengambil seluruh alokasi distribusi."""
        return DistribusiModel.get_all()

    @staticmethod
    def tambah_distribusi(id_panen, tujuan, jumlah):
        """Membuat alokasi pengiriman baru.

        Status awal otomatis bernilai "Diproses" (BR-04). Pemeriksaan
        ketersediaan stok dijalankan di dalam satu transaksi dengan
        penguncian baris sehingga tidak ada kemungkinan stok minus
        akibat dua permintaan yang berjalan bersamaan.
        """
        if not id_panen or not tujuan or not jumlah:
            return False, "ID Panen, Tujuan, dan Jumlah Dikirim wajib diisi!"

        tujuan = (tujuan or "").strip()
        if len(tujuan) > 150:
            return False, "Tujuan pengiriman maksimal 150 karakter!"

        try:
            j_float = float(jumlah)
        except (TypeError, ValueError):
            return False, "Jumlah dikirim harus berupa angka!"
        if j_float <= 0:
            return False, "Jumlah dikirim harus lebih dari 0!"

        hasil = DistribusiModel.create_with_stock_check(
            id_panen, tujuan, Decimal(str(j_float)), STATUS_DIPROSES
        )
        if not hasil[0]:
            return False, hasil[1]

        return True, "Alokasi pengiriman berhasil dibuat (Status Awal: Diproses)!"

    @staticmethod
    def update_distribusi(id_distribusi, id_panen, tujuan, jumlah, status):
        """Memperbarui alokasi distribusi beserta statusnya."""
        if not id_distribusi:
            return False, "Pilih data distribusi yang ingin diubah!"
        if not id_panen or not tujuan or not jumlah:
            return False, "ID Panen, Tujuan, dan Jumlah Dikirim wajib diisi!"

        tujuan = (tujuan or "").strip()
        if len(tujuan) > 150:
            return False, "Tujuan pengiriman maksimal 150 karakter!"

        try:
            j_float = float(jumlah)
        except (TypeError, ValueError):
            return False, "Jumlah dikirim harus berupa angka!"
        if j_float <= 0:
            return False, "Jumlah dikirim harus lebih dari 0!"

        # BR-05: status harus salah satu dari tiga nilai baku
        if status not in STATUS_PENGIRIMAN:
            return False, "Status pengiriman tidak dikenali!"

        hasil = DistribusiModel.update_with_stock_check(
            id_distribusi, id_panen, tujuan, Decimal(str(j_float)), status
        )
        if not hasil[0]:
            return False, hasil[1]
        return True, hasil[1]

    @staticmethod
    def ubah_status_distribusi(id_distribusi, status):
        """Mengubah status pengiriman tanpa mengubah data lain (BR-05, BR-09)."""
        if not id_distribusi:
            return False, "Pilih data distribusi yang ingin diubah!"
        if status not in STATUS_PENGIRIMAN:
            return False, "Status pengiriman tidak dikenali!"

        alokasi = DistribusiModel.get_by_id(id_distribusi)
        if not alokasi:
            return False, "Data distribusi tidak ditemukan!"
        if DistribusiModel.is_locked(alokasi["status_pengiriman"]):
            return False, (
                "Alokasi berstatus 'Terkirim' bersifat final dan tidak dapat diubah (BR-09)."
            )

        if not DistribusiModel.update(
            id_distribusi,
            alokasi["id_panen"],
            alokasi["tujuan_pengiriman"],
            alokasi["jumlah_dikirim"],
            status,
        ):
            return False, "Gagal memperbarui status pengiriman!"
        return True, "Status pengiriman berhasil diperbarui menjadi '%s'!" % status

    @staticmethod
    def hapus_distribusi(id_distribusi):
        """Menghapus alokasi distribusi.

        Hak penghapusan data dibatasi untuk peran Administrator saja.
        """
        if not id_distribusi:
            return False, "Pilih data distribusi yang ingin dihapus!"
        if not AuthController.boleh("bisa_hapus_data"):
            return False, (
                "Penghapusan data hanya dapat dilakukan oleh Administrator!"
            )
        return DistribusiModel.delete(id_distribusi)

    # ========================================================
    # DASHBOARD  (FR-02)
    # ========================================================
    @staticmethod
    def get_statistik():
        """Mengambil ringkasan statistik untuk kartu Dashboard.

        Nilai indikator kinerja dihitung dari data nyata, bukan
        angka tetap, sehingga selalu mencerminkan kondisi gudang
        terkini.
        """
        total_petani = PetaniModel.count()
        total_panen = PanenModel.count()
        total_distribusi = DistribusiModel.count()

        total_berat = PanenModel.total_berat()
        total_kirim = DistribusiModel.total_dikirim()
        sisa_gudang = total_berat - total_kirim

        # 1) Rasio komoditas yang sudah dialokasikan terhadap total setoran
        rasio_alokasi = float(total_kirim / total_berat) if total_berat > 0 else 0.0

        # 2) Efisiensi pengiriman: alokasi yang sudah selesai dikirim
        terkirim = DistribusiModel.count_by_status(STATUS_TERKIRIM)
        rasio_terkirim = float(terkirim / total_distribusi) if total_distribusi > 0 else 0.0

        # 3) Tingkat engage petani: petani yang pernah menyetor hasil panen
        petani_aktif = PetaniModel.count_petani_aktif()

        return {
            "total_petani": total_petani,
            "total_panen": total_panen,
            "total_distribusi": total_distribusi,
            "total_berat": total_berat,
            "total_kirim": total_kirim,
            "sisa_gudang": sisa_gudang,
            "petani_aktif": petani_aktif,
            "indikator": [
                ("Alokasi Terdistribusi", min(rasio_alokasi, 1.0)),
                ("Pengiriman Selesai", min(rasio_terkirim, 1.0)),
                (
                    "Petani Aktif",
                    min((petani_aktif / total_petani) if total_petani else 0.0, 1.0),
                ),
            ],
        }

    # ========================================================
    # PEMBANTU
    # ========================================================
    @staticmethod
    def _validasi_tanggal(tanggal):
        """Memvalidasi dan menormalkan tanggal. Mengembalikan str atau None."""
        try:
            dt = datetime.strptime((tanggal or "").strip(), FORMAT_TANGGAL)
        except (TypeError, ValueError):
            return None
        if dt.date() > datetime.now().date():
            return None
        return dt.strftime(FORMAT_TANGGAL)
