"""
==========================================================
PENGUJIAN MODEL AGRIUNO - LAPIS DATA (Modul 4)
==========================================================
Pengujian integrasi lapis model terhadap basis data MySQL sungguhan.

Berkas ini menggantikan skrip uji manual versi UTS yang hanya
menampilkan data ke terminal. Seluruh pengujian pada berkas ini
memerlukan server MySQL aktif, sehingga ditandai dengan penanda
``db`` dan otomatis dilewati apabila basis data tidak tersedia::

    pytest -v -m db
    python test_model.py        # eksekusi langsung sebagai skrip
"""

import sys

import pytest

from AgriUno_UTS_RPL.models.distribusi_model import DistribusiModel
from AgriUno_UTS_RPL.models.panen_model import PanenModel
from AgriUno_UTS_RPL.models.petani_model import PetaniModel
from AgriUno_UTS_RPL.models.user_model import UserModel


@pytest.mark.db
class TestModelPetani:
    """Pengujian integrasi tabel ``petani``."""

    def test_get_all_mengembalikan_daftar(self):
        """Tabel petani harus dapat dibaca dan menghasilkan daftar baris."""
        data = PetaniModel.get_all()
        assert isinstance(data, list)
        for baris in data:
            assert "id_petani" in baris
            assert "nama_petani" in baris
            assert "lokasi_lahan" in baris
            assert "komoditas_utama" in baris

    def test_jumlah_petani_konsisten(self):
        """Jumlah baris hasil pembacaan harus sama dengan hasil COUNT()."""
        assert len(PetaniModel.get_all()) == PetaniModel.count()


@pytest.mark.db
class TestModelPanen:
    """Pengujian integrasi tabel ``inventori_panen``."""

    def test_get_all_menyertakan_sisa_stok(self):
        """Setiap lot panen harus menyertakan perhitungan sisa stok."""
        data = PanenModel.get_all()
        assert isinstance(data, list)
        for baris in data:
            assert "jumlah_berat" in baris
            assert "sisa_stok" in baris

    def test_sisa_stok_tidak_pernah_negatif(self):
        """Sisa stok tidak boleh bernilai negatif (BR-02)."""
        for baris in PanenModel.get_all():
            assert float(baris["sisa_stok"]) >= 0


@pytest.mark.db
class TestModelDistribusi:
    """Pengujian integrasi tabel ``distribusi``."""

    def test_get_all_mengembalikan_daftar(self):
        """Tabel distribusi harus dapat dibaca dan menghasilkan daftar baris."""
        data = DistribusiModel.get_all()
        assert isinstance(data, list)
        for baris in data:
            assert "id_distribusi" in baris
            assert "status_pengiriman" in baris

    def test_status_hanya_nilai_baku(self):
        """Setiap status harus merupakan salah satu dari tiga nilai baku (BR-05)."""
        from config.constants import STATUS_PENGIRIMAN

        for baris in DistribusiModel.get_all():
            assert baris["status_pengiriman"] in STATUS_PENGIRIMAN


@pytest.mark.db
class TestModelUser:
    """Pengujian integrasi tabel ``users``."""

    def test_autentikasi_admin_demo(self):
        """Akun admin demo harus dapat diautentikasi."""
        hasil = UserModel.authenticate("admin", "admin123")
        assert hasil is not None
        assert hasil["role"] == "admin"

    def test_autentikasi_password_salah_ditolak(self):
        """Password yang salah harus ditolak."""
        assert UserModel.authenticate("admin", "passwordsalah") is None

    def test_autentikasi_username_tidak_ada_ditolak(self):
        """Username yang tidak terdaftar harus ditolak."""
        assert UserModel.authenticate("tidakada99", "apa_saja") is None


def main():
    """Menjalankan ringkasan manual pengujian model."""
    print("=" * 66)
    print("PENGUJIAN MODEL AGRIUNO - LAPIS DATA")
    print("=" * 66)

    try:
        petani = PetaniModel.get_all()
        print("\n[1] PetaniModel.get_all()")
        print("    Berhasil! Ditemukan %d data petani." % len(petani))
        for baris in petani:
            print(
                "      #%s %s (%s)"
                % (baris["id_petani"], baris["nama_petani"], baris["komoditas_utama"])
            )

        panen = PanenModel.get_all()
        print("\n[2] PanenModel.get_all()")
        print("    Berhasil! Ditemukan %d lot panen." % len(panen))
        for baris in panen:
            print(
                "      #%s %-16s berat=%8s sisa=%8s"
                % (
                    baris["id_panen"],
                    baris["jenis_komoditas"],
                    baris["jumlah_berat"],
                    baris["sisa_stok"],
                )
            )

        distribusi = DistribusiModel.get_all()
        print("\n[3] DistribusiModel.get_all()")
        print("    Berhasil! Ditemukan %d alokasi." % len(distribusi))
        for baris in distribusi:
            print(
                "      #%s lot=%s %-26s %8s Kg [%s]"
                % (
                    baris["id_distribusi"],
                    baris["id_panen"],
                    baris["tujuan_pengiriman"],
                    baris["jumlah_dikirim"],
                    baris["status_pengiriman"],
                )
            )

        print("\n[4] UserModel.authenticate('admin', 'admin123')")
        pengguna = UserModel.authenticate("admin", "admin123")
        if pengguna:
            print("    Berhasil! %s (%s)" % (pengguna["full_name"], pengguna["role"]))
        else:
            print("    Gagal login. Pastikan database.sql sudah dijalankan.")

        print("\n" + "=" * 66)
        print("PENGUJIAN MODEL SELESAI")
        print("=" * 66)
        return 0
    except Exception as exc:  # noqa: BLE001
        print("\nGagal menjalankan pengujian model: %s" % exc)
        print("Pastikan layanan MySQL pada Laragon sedang aktif.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
