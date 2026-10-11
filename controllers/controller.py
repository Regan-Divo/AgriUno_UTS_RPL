# ==========================================
# CONTROLLER UTAMA - AGRIUNO
# ==========================================
from models.petani_model import PetaniModel
from models.panen_model import PanenModel
from models.distribusi_model import DistribusiModel

class AgriUnoController:
    @staticmethod
    def get_petani(): return PetaniModel.get_all_petani()
    
    @staticmethod
    def simpan_petani(nama, lokasi, komoditas):
        if nama and lokasi and komoditas:
            return PetaniModel.tambah_petani(nama, lokasi, komoditas)
        return False

    @staticmethod
    def get_panen(): return PanenModel.get_all_panen()
    
    @staticmethod
    def simpan_panen(id_p, jenis_komoditas, jumlah_berat, tgl_panen):
        if id_p and jenis_komoditas and jumlah_berat and tgl_panen:
            try:
                return PanenModel.tambah_panen(int(id_p), jenis_komoditas, float(jumlah_berat), tgl_panen)
            except ValueError:
                return False
        return False

    @staticmethod
    def get_distribusi(): return DistribusiModel.get_all_distribusi()
    
    @staticmethod
    def simpan_distribusi(id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman):
        if id_panen and tujuan_pengiriman and jumlah_dikirim:
            try:
                return DistribusiModel.tambah_distribusi(int(id_panen), tujuan_pengiriman, float(jumlah_dikirim), status_pengiriman)
            except ValueError:
                return False
        return False