import re
from models.petani_model import PetaniModel
from models.panen_model import PanenModel
from models.distribusi_model import DistribusiModel

class PetaniController:
    TEXT_PATTERN = r"^[a-zA-Z0-9\s\.,\-]+$"

    @staticmethod
    def validasiInput(nama, lokasi, komoditas):
        if not nama or not lokasi or not komoditas:
            return False, "Semua field pada form petani harus diisi!"
        return True, "Validasi sukses."

    @classmethod
    def simpanPetani(cls, nama, lokasi, komoditas):
        valid, msg = cls.validasiInput(nama, lokasi, komoditas)
        if not valid:
            return False, msg
        return PetaniModel.tambah_petani(nama, lokasi, komoditas)

    @staticmethod
    def tambah_petani(nama, lokasi, komoditas):
        return PetaniController.simpanPetani(nama, lokasi, komoditas)

    @staticmethod
    def update_petani(id_petani, nama, lokasi, komoditas):
        if not id_petani:
            return False, "ID Petani tidak valid!"
        return PetaniModel.update_petani(int(id_petani), nama, lokasi, komoditas)

    @staticmethod
    def delete_petani(id_petani):
        if not id_petani:
            return False, "ID Petani tidak valid!"
        return PetaniModel.delete_petani(int(id_petani))

    @staticmethod
    def get_petani():
        return PetaniModel.get_all_petani()


class InventoriController:
    @classmethod
    def simpanPanen(cls, id_petani, komoditas, berat):
        if not id_petani or not komoditas or not berat:
            return False, "Semua field inventori panen harus diisi!"
        try:
            id_p = int(id_petani)
            b = float(berat)
            if b <= 0:
                return False, "Jumlah berat harus lebih besar dari 0."
        except ValueError:
            return False, "ID Petani dan Jumlah Berat harus berupa angka yang valid."
        return PanenModel.tambah_panen(id_p, komoditas, b)

    @staticmethod
    def tambah_panen(id_petani, komoditas, berat):
        return InventoriController.simpanPanen(id_petani, komoditas, berat)

    @staticmethod
    def delete_panen(id_panen):
        if not id_panen:
            return False, "ID Panen tidak valid!"
        return PanenModel.delete_panen(int(id_panen))

    @staticmethod
    def getStok(filter_komoditas=""):
        all_panen = PanenModel.get_all_panen()
        if not filter_komoditas:
            return all_panen
        return [p for p in all_panen if filter_komoditas.lower() in p['jenis_komoditas'].lower()]

    @staticmethod
    def get_panen():
        return PanenModel.get_all_panen()


class DistribusiController:
    @classmethod
    def alokasiPengiriman(cls, id_panen, tujuan, jumlah):
        if not id_panen or not tujuan or not jumlah:
            return False, "Semua field distribusi harus diisi!"
        try:
            id_p = int(id_panen)
            j = float(jumlah)
            if j <= 0:
                return False, "Jumlah kirim harus lebih besar dari 0."
        except ValueError:
            return False, "ID Panen dan Jumlah Kirim harus berupa angka yang valid."
        return DistribusiModel.tambah_distribusi(id_p, tujuan, j)

    @staticmethod
    def tambah_distribusi(id_panen, tujuan, jumlah):
        return DistribusiController.alokasiPengiriman(id_panen, tujuan, jumlah)

    @staticmethod
    def updateStatus(id_distribusi, status_baru="Diproses"):
        if not id_distribusi:
            return False, "ID Distribusi tidak valid!"
        return DistribusiModel.delete_distribusi(int(id_distribusi))

    @staticmethod
    def delete_distribusi(id_distribusi):
        return DistribusiController.updateStatus(id_distribusi)

    @staticmethod
    def get_distribusi():
        return DistribusiModel.get_all_distribusi()