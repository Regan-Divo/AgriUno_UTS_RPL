"""
==========================================================
CONTROLLER UTAMA - AGRIUNO
==========================================================
"""
from models.petani_model import PetaniModel
from models.panen_model import PanenModel
from models.distribusi_model import DistribusiModel
from config.database import DatabaseConnection

class AgriUnoController:
    # --- Petani Logic ---
    @staticmethod
    def get_petani():
        return PetaniModel.get_all()

    @staticmethod
    def tambah_petani(nama, lokasi, komoditas):
        if not nama or not lokasi or not komoditas:
            return False, "Nama, lokasi lahan, dan komoditas utama wajib diisi!"
        PetaniModel.insert(nama, lokasi, komoditas)
        return True, "Data petani berhasil disimpan!"

    @staticmethod
    def update_petani(id_petani, nama, lokasi, komoditas):
        if not id_petani: return False, "Pilih data petani yang ingin diubah!"
        PetaniModel.update(id_petani, nama, lokasi, komoditas)
        return True, "Data petani berhasil diperbarui!"

    @staticmethod
    def hapus_petani(id_petani):
        if not id_petani: return False, "Pilih data petani yang ingin dihapus!"
        return PetaniModel.delete(id_petani)

    # --- Panen Logic ---
    @staticmethod
    def get_panen():
        return PanenModel.get_all()

    @staticmethod
    def tambah_panen(id_petani, jenis, berat, tanggal):
        if not id_petani or not jenis or not berat or not tanggal:
            return False, "Seluruh kolom setoran panen wajib diisi!"
        try:
            b_float = float(berat)
            if b_float <= 0: return False, "Jumlah berat panen harus berupa angka positif!"
        except ValueError:
            return False, "Jumlah berat harus berupa angka numerik!"
            
        PanenModel.insert(id_petani, jenis, berat, tanggal)
        return True, "Setoran panen berhasil dicatat!"

    @staticmethod
    def update_panen(id_panen, id_petani, jenis, berat, tanggal):
        if not id_panen: return False, "Pilih data panen yang ingin diubah!"
        PanenModel.update(id_panen, id_petani, jenis, berat, tanggal)
        return True, "Data panen berhasil diperbarui!"

    @staticmethod
    def hapus_panen(id_panen):
        if not id_panen: return False, "Pilih lot panen yang ingin dihapus!"
        return PanenModel.delete(id_panen)

    # --- Distribusi Logic (Validasi Sisa Stok BR-02 & Status Awal 'Diproses' BR-04) ---
    @staticmethod
    def get_distribusi():
        return DistribusiModel.get_all()

    @staticmethod
    def tambah_distribusi(id_panen, tujuan, jumlah):
        if not id_panen or not tujuan or not jumlah:
            return False, "ID Panen, Tujuan, dan Jumlah Dikirim wajib diisi!"
        try:
            j_float = float(jumlah)
            if j_float <= 0: return False, "Jumlah dikirim harus lebih dari 0!"
        except ValueError:
            return False, "Jumlah dikirim harus berupa angka!"
            
        # Validasi ketersediaan stok (Aturan Bisnis BR-02)
        conn = DatabaseConnection.connect()
        if not conn: return False, "Koneksi database gagal!"
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT jumlah_berat FROM inventori_panen WHERE id_panen = %s", (id_panen,))
        panen = cursor.fetchone()
        
        if not panen:
            cursor.close(); conn.close()
            return False, "ID Panen tidak terdaftar di sistem!"
            
        total_berat = float(panen['jumlah_berat'])
        
        cursor.execute("SELECT SUM(jumlah_dikirim) as total_kirim FROM distribusi WHERE id_panen = %s", (id_panen,))
        dist = cursor.fetchone()
        sudah_kirim = float(dist['total_kirim']) if dist['total_kirim'] is not None else 0.0
        
        cursor.close(); conn.close()
        
        sisa_stok = total_berat - sudah_kirim
        
        if j_float > sisa_stok:
            return False, f"Jumlah kirim melebihi sisa stok inventori yang tersedia di gudang! (Sisa: {sisa_stok:.2f} Kg)"
            
        DistribusiModel.insert(id_panen, tujuan, j_float, status="Diproses")
        return True, "Alokasi pengiriman berhasil dibuat (Status Awal: Diproses)!"

    @staticmethod
    def update_distribusi(id_distribusi, id_panen, tujuan, jumlah, status):
        if not id_distribusi: return False, "Pilih data distribusi yang ingin diubah!"
        if not status: status = "Diproses"
        DistribusiModel.update(id_distribusi, id_panen, tujuan, jumlah, status)
        return True, "Data distribusi berhasil diperbarui!"

    @staticmethod
    def hapus_distribusi(id_distribusi):
        if not id_distribusi: return False, "Pilih data distribusi yang ingin dihapus!"
        DistribusiModel.delete(id_distribusi)
        return True, "Alokasi distribusi berhasil dihapus!"