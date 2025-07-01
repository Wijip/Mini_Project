jumlah_angka = int(input("Masukkan jumlah angka yang akan diperiksa: "))
for i in range(jumlah_angka):
    angka = int(input(f"Masukkan angka ke-{i + 1}: "))
    if angka % 2 == 0:
        print(f"{angka} adalah bilangan genap")
    else:
        print(f"{angka} adalah bilangan ganjil")
print("Selesai memproses semua angka")