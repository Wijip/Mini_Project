import json
import os
from cryptography.fernet import Fernet

FILE_NAME = 'password.json'
KEY_FILE = 'secret.key'

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

key = load_key()
cipher = Fernet(key)

def ensure_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as f:
            json.dump({}, f)

def save_password(service, username, password):
    ensure_file()
    encrypted_password = cipher.encrypt(password.encode()).decode()

    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        data[service].append({"username": username, "password":encrypted_password})
    else:
        data[service] = [{"username": username, "password":encrypted_password}]
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Kata sandi untuk '{service}' telah disimpan.")

def get_password(service):
    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        print(f"\n🔐 Akun-Akun untuk '{service}':")
        for i, account in enumerate(data[service], start=1):
            encrypted_password = account["password"]
            decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
            print(f"{i}. username: {account['username']}, password: {decrypted_password}")
    else:
        print("❌ Data tidak ditemukan!")

while True:
    print("\n======== Password Manager ========")
    print("1. Simpan kata sandi")
    print("2. Baca kata sandi")
    print("0. Keluar")
    pilih = int(input("Masukkan Pilihan: "))
    try:
        if pilih == 1:
            service = input("Masukkan nama layanan : ")
            username = input("Masukkan Username/Email : ")
            password = input("masukkan Kata Sandi : ")
            save_password(service, username, password)
        elif pilih == 2:
            service = input("Masukkan nama layanan : ")
            get_password(service)
        elif pilih == 0:
            print("🚀 Terima kasih telah menggunakan Password Manager!")
            break
        else:
            print("❌ Pilihan tidak valid. coba lagi.")
    except ValueError:
        print("❌ Harap masukkan angka yang valid")