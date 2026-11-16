"""
==========================================================
PENGUJIAN OTOMATIS - LOGIKA BISNIS AgriUno (Modul 6)
==========================================================
Pengujian unit untuk lapisan Controller beserta aturan bisnis
BR-01 sampai BR-11.

Seluruh pengujian pada berkas ini tidak memerlukan server MySQL
karena pemanggilan ke model ditirukan menggunakan monkeypatch.
Pengujian yang memang harus menyentuh basis data ditandai dengan
penanda ``@pytest.mark.db`` dan diletakkan pada berkas terpisah.
"""

import pytest

from config.constants import STATUS_DIPROSES, STATUS_TERKIRIM
from controllers.controller import AgriUnoController


# ============================================================
# 1. VALIDASI DATA PETANI
# ============================================================
class TestPetani:
    """Pengujian validasi form data petani."""

    def test_tambah_petani_gagal_bila_kolom_kosong(self):
        """Ketiga kolom wajib diisi."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_petani("", "Lokasi", "Padi")
        assert berhasil is False
        assert "wajib diisi" in pesan

    def test_tambah_petani_gagal_bila_nama_hanya_spasi(self):
        """Spasi saja dianggap kosong."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, _ = AgriUnoController.tambah_petani("   ", "Lokasi", "Padi")
        assert berhasil is False

    def test_tambah_petani_berhasil(self):
        """Data lengkap harus berhasil disimpan."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_petani(
                "Siti Halimah", "Wonosari", "Beras Organik"
            )
        assert berhasil is True
        assert "berhasil disimpan" in pesan

    def test_tambah_petani_menolak_nama_terlalu_panjang(self):
        """Panjang teks dibatasi sesuai kolom basis data."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_petani("A" * 101, "Wonosari", "Beras")
        assert berhasil is False
        assert "maksimal 100" in pesan

    def test_update_petani_menolak_kolom_kosong(self):
        """Pembaruan juga memvalidasi kelengkapan kolom."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "update", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.update_petani(1, "Siti", "", "Beras")
        assert berhasil is False
        assert "wajib diisi" in pesan

    def test_update_petani_menolak_id_kosong(self):
        """ID petani tidak boleh kosong saat pembaruan."""
        berhasil, pesan = AgriUnoController.update_petani(None, "Siti", "Wonosari", "Beras")
        assert berhasil is False
        assert "Pilih data" in pesan

    # ------------------------------------------------------------
    # BR-11: keunikan data petani dan penulisan baku
    # ------------------------------------------------------------
    @staticmethod
    def _petani_contoh():
        """Data petani tiruan untuk pemeriksaan duplikat."""
        return [
            {
                "id_petani": 1,
                "nama_petani": "Siti Halimah",
                "lokasi_lahan": "Wonosari",
                "komoditas_utama": "Beras Organik",
            },
            {
                "id_petani": 2,
                "nama_petani": "Budi Santoso",
                "lokasi_lahan": "Palu",
                "komoditas_utama": "Jeruk",
            },
        ]

    def test_tambah_petani_menolak_data_identik(self):
        """BR-11: kombinasi nama, lokasi, dan komoditas wajib unik."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "insert", staticmethod(lambda *a, **k: True))
            mp.setattr(
                PetaniModel,
                "get_all",
                staticmethod(lambda *a, **k: TestPetani._petani_contoh()),
            )
            berhasil, pesan = AgriUnoController.tambah_petani(
                "Siti Halimah", "Wonosari", "Beras Organik"
            )
        assert berhasil is False
        assert "sudah terdaftar" in pesan
        assert "BR-11" in pesan

    def test_tambah_petani_duplikat_tidak_peka_kapitalisasi(self):
        """BR-11: "JERUK" dianggap sama dengan "Jeruk"."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "insert", staticmethod(lambda *a, **k: True))
            mp.setattr(
                PetaniModel,
                "get_all",
                staticmethod(lambda *a, **k: TestPetani._petani_contoh()),
            )
            berhasil, pesan = AgriUnoController.tambah_petani("budi  santoso", "PALU", "JERUK")
        assert berhasil is False
        assert "sudah terdaftar" in pesan

    def test_update_petani_mengizinkan_data_sendiri(self):
        """BR-11: pembaruan tanpa perubahan tidak dianggap duplikat."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "exists", staticmethod(lambda *a, **k: True))
            mp.setattr(PetaniModel, "update", staticmethod(lambda *a, **k: True))
            mp.setattr(
                PetaniModel,
                "get_all",
                staticmethod(lambda *a, **k: TestPetani._petani_contoh()),
            )
            berhasil, pesan = AgriUnoController.update_petani(
                1, "Siti Halimah", "Wonosari", "Beras Organik"
            )
        assert berhasil is True
        assert "berhasil diperbarui" in pesan

    def test_update_petani_menolak_duplikat_petani_lain(self):
        """BR-11: pembaruan tidak boleh meniru data petani lain."""
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PetaniModel, "exists", staticmethod(lambda *a, **k: True))
            mp.setattr(PetaniModel, "update", staticmethod(lambda *a, **k: True))
            mp.setattr(
                PetaniModel,
                "get_all",
                staticmethod(lambda *a, **k: TestPetani._petani_contoh()),
            )
            berhasil, pesan = AgriUnoController.update_petani(1, "Budi Santoso", "Palu", "Jeruk")
        assert berhasil is False
        assert "sudah terdaftar" in pesan

    def test_norm_teks_menormalkan_spasi_dan_kapital(self):
        """BR-11: teks isian dirapatkan dan diubah kapitalisasi judul."""
        assert AgriUnoController._norm_teks("  JERUK   manis  ") == "Jeruk Manis"
        assert AgriUnoController._norm_teks("siti   halimah") == "Siti Halimah"
        assert AgriUnoController._norm_teks(None) == ""

    def test_tambah_panen_menormalkan_jenis_komoditas(self):
        """Jenis komoditas dinormalkan sebelum disimpan (BR-11)."""
        from models.panen_model import PanenModel
        from models.petani_model import PetaniModel

        tersimpan = {}

        def tiruan_insert(id_petani, jenis, berat, tanggal):
            tersimpan["jenis"] = jenis
            return True

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(tiruan_insert))
            mp.setattr(PetaniModel, "exists", staticmethod(lambda *a, **k: True))
            berhasil, _ = AgriUnoController.tambah_panen(1, "  BERAS  organik ", "10", "2026-01-01")
        assert berhasil is True
        assert tersimpan["jenis"] == "Beras Organik"

    def test_hapus_petani_menolak_id_kosong(self):
        """ID petani tidak boleh kosong saat penghapusan."""
        berhasil, pesan = AgriUnoController.hapus_petani(None)
        assert berhasil is False
        assert "Pilih data" in pesan

    def test_hapus_petani_ditolak_tanpa_hak_hapus(self):
        """RBAC: peran tanpa hak hapus (operator/petani) ditolak."""
        from controllers.auth_controller import AuthController
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                AuthController, "boleh", staticmethod(lambda cap: cap == "bisa_kelola_petani")
            )
            mp.setattr(
                PetaniModel, "delete",
                staticmethod(lambda *a, **k: pytest.fail("Model tidak boleh dipanggil")),
            )
            berhasil, pesan = AgriUnoController.hapus_petani(1)
        assert berhasil is False
        assert "Administrator" in pesan

    def test_hapus_panen_ditolak_tanpa_hak_hapus(self):
        """RBAC: penghapusan lot panan juga dibatasi Administrator."""
        from controllers.auth_controller import AuthController
        from models.panen_model import PanenModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(AuthController, "boleh", staticmethod(lambda cap: False))
            mp.setattr(
                PanenModel, "delete",
                staticmethod(lambda *a, **k: pytest.fail("Model tidak boleh dipanggil")),
            )
            berhasil, pesan = AgriUnoController.hapus_panen(1)
        assert berhasil is False
        assert "Administrator" in pesan

    def test_hapus_distribusi_ditolak_tanpa_hak_hapus(self):
        """RBAC: penghapusan alokasi juga dibatasi Administrator."""
        from controllers.auth_controller import AuthController
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(AuthController, "boleh", staticmethod(lambda cap: False))
            mp.setattr(
                DistribusiModel, "delete",
                staticmethod(lambda *a, **k: pytest.fail("Model tidak boleh dipanggil")),
            )
            berhasil, pesan = AgriUnoController.hapus_distribusi(1)
        assert berhasil is False
        assert "Administrator" in pesan


# ============================================================
# 2. VALIDASI DATA PANEN
# ============================================================
class TestPanen:
    """Pengujian validasi form setoran panen."""

    def test_tambah_panen_gagal_bila_kolom_kosong(self):
        """Seluruh kolom wajib diisi."""
        from models.panen_model import PanenModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_panen(1, "Padi", "", "2026-10-02")
        assert berhasil is False
        assert "wajib diisi" in pesan

    def test_tambah_panen_menolak_berat_non_numerik(self):
        """Berat harus berupa angka."""
        from models.panen_model import PanenModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_panen(1, "Padi", "abc", "2026-10-02")
        assert berhasil is False
        assert "numerik" in pesan

    def test_tambah_panen_menolak_berat_nol_atau_negatif(self):
        """Berat harus lebih besar dari nol."""
        from models.panen_model import PanenModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_panen(1, "Padi", "-5", "2026-10-02")
        assert berhasil is False
        assert "positif" in pesan

    def test_tambah_panen_menolak_tanggal_tidak_valid(self):
        """Tanggal harus berformat YYYY-MM-DD."""
        from models.panen_model import PanenModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_panen(1, "Padi", "10", "02-10-2026")
        assert berhasil is False
        assert "YYYY-MM-DD" in pesan

    def test_tambah_panen_menolak_tanggal_masa_depan(self):
        """Tanggal panen tidak boleh berada di masa depan."""
        from models.panen_model import PanenModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_panen(1, "Padi", "10", "2099-01-01")
        assert berhasil is False
        assert "YYYY-MM-DD" in pesan

    def test_tambah_panen_menolak_petani_tidak_terdaftar(self):
        """BR-01: penyetor wajib terdaftar pada tabel petani."""
        from models.panen_model import PanenModel
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(lambda *a, **k: True))
            mp.setattr(PetaniModel, "exists", staticmethod(lambda *a, **k: False))
            berhasil, pesan = AgriUnoController.tambah_panen(99, "Padi", "10", "2026-10-02")
        assert berhasil is False
        assert "tidak terdaftar" in pesan

    def test_tambah_panen_berhasil(self):
        """Data lengkap dan valid harus berhasil disimpan."""
        from models.panen_model import PanenModel
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "insert", staticmethod(lambda *a, **k: True))
            mp.setattr(PetaniModel, "exists", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.tambah_panen(
                1, "Beras Organik", "320.50", "2026-10-02"
            )
        assert berhasil is True
        assert "berhasil dicatat" in pesan

    def test_update_panen_menolak_berat_kurang_dari_alokasi(self):
        """BR-02: berat baru tidak boleh lebih kecil dari total alokasi."""
        from decimal import Decimal

        from models.panen_model import PanenModel
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "update", staticmethod(lambda *a, **k: True))
            mp.setattr(PanenModel, "get_by_id", staticmethod(lambda *a, **k: {"id_panen": 1}))
            mp.setattr(
                PanenModel, "get_total_terkirim", staticmethod(lambda *a, **k: Decimal("150.00"))
            )
            mp.setattr(PetaniModel, "exists", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.update_panen(
                1, 1, "Beras Organik", "100", "2026-10-02"
            )
        assert berhasil is False
        assert "dialokasikan" in pesan

    def test_update_panen_berhasil(self):
        """Pembaruan dengan berat yang wajar harus berhasil."""
        from decimal import Decimal

        from models.panen_model import PanenModel
        from models.petani_model import PetaniModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(PanenModel, "update", staticmethod(lambda *a, **k: True))
            mp.setattr(PanenModel, "get_by_id", staticmethod(lambda *a, **k: {"id_panen": 1}))
            mp.setattr(
                PanenModel, "get_total_terkirim", staticmethod(lambda *a, **k: Decimal("50.00"))
            )
            mp.setattr(PetaniModel, "exists", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.update_panen(
                1, 1, "Beras Organik", "200", "2026-10-02"
            )
        assert berhasil is True
        assert "diperbarui" in pesan


# ============================================================
# 3. VALIDASI DATA DISTRIBUSI
# ============================================================
class TestDistribusi:
    """Pengujian validasi form alokasi distribusi."""

    def test_tambah_distribusi_gagal_bila_kolom_kosong(self):
        """Seluruh kolom wajib diisi."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel, "create_with_stock_check", staticmethod(lambda *a, **k: (True, 1))
            )
            berhasil, pesan = AgriUnoController.tambah_distribusi(1, "", "10")
        assert berhasil is False
        assert "wajib diisi" in pesan

    def test_tambah_distribusi_menolak_jumlah_non_numerik(self):
        """Jumlah kirim harus berupa angka."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel, "create_with_stock_check", staticmethod(lambda *a, **k: (True, 1))
            )
            berhasil, pesan = AgriUnoController.tambah_distribusi(1, "Pasar", "abc")
        assert berhasil is False
        assert "angka" in pesan

    def test_tambah_distribusi_menolak_jumlah_nol(self):
        """Jumlah kirim harus lebih dari nol."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel, "create_with_stock_check", staticmethod(lambda *a, **k: (True, 1))
            )
            berhasil, pesan = AgriUnoController.tambah_distribusi(1, "Pasar", "0")
        assert berhasil is False
        assert "lebih dari 0" in pesan

    def test_tambah_distribusi_meneruskan_gagal_validasi_stok(self):
        """Pesan penolakan dari model harus diteruskan ke pengguna."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel,
                "create_with_stock_check",
                staticmethod(lambda *a, **k: (False, "Sisa stok tidak cukup.")),
            )
            berhasil, pesan = AgriUnoController.tambah_distribusi(1, "Pasar", "500")
        assert berhasil is False
        assert "stok" in pesan

    def test_tambah_distribusi_berhasil_dengan_status_awal(self):
        """BR-04: status awal alokasi harus "Diproses"."""
        from models.distribusi_model import DistribusiModel

        captured = {}

        def fake_create(id_panen, tujuan, jumlah, status=STATUS_DIPROSES):
            captured["status"] = status
            return True, 1

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(DistribusiModel, "create_with_stock_check", staticmethod(fake_create))
            berhasil, pesan = AgriUnoController.tambah_distribusi(1, "Pasar", "50")
        assert berhasil is True
        assert captured["status"] == STATUS_DIPROSES
        assert "Diproses" in pesan

    def test_update_distribusi_menolak_status_tidak_dikenal(self):
        """BR-05: hanya tiga nilai status baku yang diterima."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel,
                "update_with_stock_check",
                staticmethod(lambda *a, **k: (True, "ok")),
            )
            berhasil, pesan = AgriUnoController.update_distribusi(1, 1, "Pasar", "10", "Dibatalkan")
        assert berhasil is False
        assert "tidak dikenali" in pesan

    def test_update_distribusi_menolak_jumlah_nol(self):
        """Jumlah kirim harus lebih dari nol."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel,
                "update_with_stock_check",
                staticmethod(lambda *a, **k: (True, "ok")),
            )
            berhasil, pesan = AgriUnoController.update_distribusi(
                1, 1, "Pasar", "0", STATUS_DIPROSES
            )
        assert berhasil is False
        assert "lebih dari 0" in pesan

    def test_ubah_status_menolak_status_tidak_dikenal(self):
        """Status di luar daftar baku harus ditolak."""
        berhasil, pesan = AgriUnoController.ubah_status_distribusi(1, "Selesai")
        assert berhasil is False
        assert "tidak dikenali" in pesan

    def test_ubah_status_menolak_alokasi_terkunci(self):
        """BR-09: alokasi berstatus 'Terkirim' bersifat final."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel,
                "get_by_id",
                staticmethod(
                    lambda *a, **k: {
                        "id_distribusi": 1,
                        "id_panen": 1,
                        "tujuan_pengiriman": "Pasar",
                        "jumlah_dikirim": 10,
                        "status_pengiriman": STATUS_TERKIRIM,
                    }
                ),
            )
            berhasil, pesan = AgriUnoController.ubah_status_distribusi(1, STATUS_DIPROSES)
        assert berhasil is False
        assert "final" in pesan

    def test_ubah_status_berhasil(self):
        """Perubahan status yang sah harus berhasil."""
        from models.distribusi_model import DistribusiModel

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                DistribusiModel,
                "get_by_id",
                staticmethod(
                    lambda *a, **k: {
                        "id_distribusi": 1,
                        "id_panen": 1,
                        "tujuan_pengiriman": "Pasar",
                        "jumlah_dikirim": 10,
                        "status_pengiriman": STATUS_DIPROSES,
                    }
                ),
            )
            mp.setattr(DistribusiModel, "update", staticmethod(lambda *a, **k: True))
            berhasil, pesan = AgriUnoController.ubah_status_distribusi(1, STATUS_TERKIRIM)
        assert berhasil is True
        assert STATUS_TERKIRIM in pesan

    def test_hapus_distribusi_menolak_id_kosong(self):
        """ID alokasi tidak boleh kosong saat penghapusan."""
        berhasil, pesan = AgriUnoController.hapus_distribusi(None)
        assert berhasil is False
        assert "Pilih data" in pesan


# ============================================================
# 4. VALIDASI STATUS PENGIRIMAN
# ============================================================
class TestStatusPengiriman:
    """Pengujian konsistensi nilai status pengiriman (BR-05)."""

    def test_status_baku_hanya_tiga(self):
        """Hanya tiga nilai status yang sah."""
        from config.constants import STATUS_PENGIRIMAN
        from models.distribusi_model import DistribusiModel

        assert len(STATUS_PENGIRIMAN) == 3
        assert STATUS_DIPROSES in STATUS_PENGIRIMAN
        assert STATUS_TERKIRIM in STATUS_PENGIRIMAN
        assert DistribusiModel.valid_status(STATUS_DIPROSES) is True
        assert DistribusiModel.valid_status("Dibatalkan") is False

    def test_status_terkunci_adalah_terkirim(self):
        """Status final hanya 'Terkirim' (BR-09)."""
        from models.distribusi_model import DistribusiModel

        assert DistribusiModel.is_locked(STATUS_TERKIRIM) is True
        assert DistribusiModel.is_locked(STATUS_DIPROSES) is False
