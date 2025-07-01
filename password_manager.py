import json
import os
from cryptography.fernet import Fernet

# Menentukan lokasi penyimpanan file
FILE_NAME = "passwords.json"


# Fungsi untuk menghasilkan atau membaca kunci enkripsi
def load_key():
    key_file = "secret.key"
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    else:
        with open(key_file, "rb") as f:
            key = f.read()
    return key


# Menginisialisasi kunci enkripsi
key = load_key()
cipher = Fernet(key)


# Fungsi untuk menyimpan kata sandi
def save_password(service, username, password):
    encrypted_password = cipher.encrypt(password.encode()).decode()
    data = {}

    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            data = json.load(f)

    data[service] = {"username": username, "password": encrypted_password}

    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Kata sandi untuk '{service}' telah disimpan.")


# Fungsi untuk mengambil kata sandi
def get_password(service):
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            data = json.load(f)
            if service in data:
                encrypted_password = data[service]["password"]
                decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
                print(f"🔑 Username: {data[service]['username']}")
                print(f"🔐 Password: {decrypted_password}")
                return
    print("❌ Data tidak ditemukan!")


# Program utama
while True:
    print("\n=== Password Manager ===")
    print("1. Simpan Kata Sandi")
    print("2. Ambil Kata Sandi")
    print("0. Keluar")

    choice = input("Pilih opsi: ")

    if choice == "1":
        service = input("Masukkan nama layanan: ")
        username = input("Masukkan username: ")
        password = input("Masukkan kata sandi: ")
        save_password(service, username, password)
    elif choice == "2":
        service = input("Masukkan nama layanan: ")
        get_password(service)
    elif choice == "0":
        print("🚀 Terima kasih telah menggunakan Password Manager!")
        break
    else:
        print("❌ Pilihan tidak valid. Coba lagi.")
