# ==========================================
# VALIDATOR BACKEND - AGRIUNO
# ==========================================
from models.petani_model import PetaniModel

if __name__ == "__main__":
    print("=== PENGUJIAN KONEKSI & MODEL AGRIUNO ===")
    data = PetaniModel.get_all_petani()
    print(f"Total Petani Terdaftar: {len(data)}")
    for d in data:
        print(f" - [{d['id_petani']}] {d['nama_petani']} ({d['komoditas_utama']})")