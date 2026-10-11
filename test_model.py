from models.petani_model import PetaniModel
from models.panen_model import PanenModel
from models.distribusi_model import DistribusiModel

def test_database_models():
    print("=== MENJALANKAN PENGUJIAN MODEL (TEST MODEL) ===")
    
    # 1. Menguji Model Petani
    print("\n[1] Menguji PetaniModel.get_all_petani():")
    try:
        petani_list = PetaniModel.get_all_petani()
        print(f"Berhasil! Ditemukan {len(petani_list)} data petani.")
        for p in petani_list:
            print(p)
    except Exception as e:
        print(f"Gagal memuat data petani: {e}")

    # 2. Menguji Model Inventori Panen
    print("\n[2] Menguji PanenModel.get_all_panen():")
    try:
        panen_list = PanenModel.get_all_panen()
        print(f"Berhasil! Ditemukan {len(panen_list)} data lot panen.")
        for pa in panen_list:
            print(pa)
    except Exception as e:
        print(f"Gagal memuat data panen: {e}")

    # 3. Menguji Model Distribusi
    print("\n[3] Menguji DistribusiModel.get_all_distribusi():")
    try:
        dist_list = DistribusiModel.get_all_distribusi()
        print(f"Berhasil! Ditemukan {len(dist_list)} data distribusi.")
        for d in dist_list:
            print(d)
    except Exception as e:
        print(f"Gagal memuat data distribusi: {e}")
    
    print("\n=== PENGUJIAN MODEL SELESAI ===")

if __name__ == "__main__":
    test_database_models()