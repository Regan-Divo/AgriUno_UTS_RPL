# =====================================================================
# DEMONSTRASI LENGKAP CRUD & JOIN - AGRIUNO (Modul 4)
# =====================================================================
from models.petani_model import PetaniModel
from models.panen_model import PanenModel

if _name_ == "_main_":
    print("==================================================")
    print("      DEMONSTRASI LENGKAP CRUD & JOIN AGRIUNO     ")
    print("==================================================")

    # 1. CREATE (Menambah data baru)
    print("\n[1. CREATE] Menambahkan data petani baru...")
    PetaniModel.tambah_petani("Rian Pratama", "Sidera", "Kakao")
    print("-> Data petani baru 'Rian Pratama' berhasil ditambahkan!")

    # 2. READ (Melihat seluruh data petani setelah ditambah)
    print("\n[2. READ] Daftar Seluruh Petani:")
    daftar_petani = PetaniModel.get_all_petani()
    for p in daftar_petani:
        print(f"ID: {p['id_petani']} | Nama: {p['nama_petani']} | Lokasi: {p['lokasi_lahan']} | Komoditas: {p['komoditas_utama']}")

    # Ambil ID terakhir yang baru saja dimasukkan untuk uji coba Update & Delete
    id_terakhir = daftar_petani[-1]['id_petani'] if daftar_petani else 1

    # 3. UPDATE (Mengubah data petani berdasarkan ID terakhir)
    print(f"\n[3. UPDATE] Memperbarui data petani dengan ID: {id_terakhir}...")
    PetaniModel.update_petani(id_terakhir, "Rian Pratama (Updated)", "Biromaru", "Kopi")
    print(f"-> Data petani ID {id_terakhir} berhasil diperbarui!")

    # 4. READ LAGI (Melihat perubahan setelah Update)
    print("\n[4. READ] Daftar Petani Setelah Update:")
    daftar_petani_baru = PetaniModel.get_all_petani()
    for p in daftar_petani_baru:
        print(f"ID: {p['id_petani']} | Nama: {p['nama_petani']} | Lokasi: {p['lokasi_lahan']} | Komoditas: {p['komoditas_utama']}")

    # 5. READ + JOIN (Melihat data inventori panen dengan relasi petani)
    print("\n[5. READ + JOIN] Mengambil data inventori panen & relasi tabel petani...")
    daftar_panen = PanenModel.get_all_panen()
    if not daftar_panen:
        print("Belum ada data inventori panen.")
    else:
        for panen in daftar_panen:
            print(f"ID Panen: {panen['id_panen']} | Petani: {panen['nama_petani']} | Komoditas: {panen['jenis_komoditas']} | Berat: {panen['jumlah_berat']} Kg")

    # 6. DELETE (Menghapus data uji coba yang baru dibuat menggunakan delete_petani)
    print(f"\n[6. DELETE] Menghapus data uji coba petani dengan ID: {id_terakhir}...")
    PetaniModel.delete_petani(id_terakhir)

    # 7. READ AKHIR (Melihat daftar petani setelah data dihapus)
    print("\n[7. READ] Daftar Petani Setelah Penghapusan (Final):")
    daftar_petani_akhir = PetaniModel.get_all_petani()
    for p in daftar_petani_akhir:
        print(f"ID: {p['id_petani']} | Nama: {p['nama_petani']} | Lokasi: {p['lokasi_lahan']} | Komoditas: {p['komoditas_utama']}")

    print("\n==================================================")
    print("      DEMONSTRASI CRUD & JOIN SELESAI !           ")