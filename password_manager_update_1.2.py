import json
import os
import re
from cryptography.fernet import Fernet

FILE_NAME = "password.json"
KEY_FILE = "secret.key"


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


# Fungsi untuk validasi keamanan kata sandi
def validate_password(password):
    if len(password) < 8:
        print("❌ Kata sandi harus memiliki minimal 8 karakter.")
        return False
    if not re.search(r"[A-Z]", password):
        print("❌ Kata sandi harus mengandung huruf besar.")
        return False
    if not re.search(r"[a-z]", password):
        print("❌ Kata sandi harus mengandung huruf kecil.")
        return False
    if not re.search(r"\d", password):
        print("❌ Kata sandi harus mengandung angka.")
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        print("❌ Kata sandi harus mengandung simbol spesial.")
        return False
    return True


def save_password(service, username, password):
    ensure_file()
    if not validate_password(password):  # Memastikan password valid
        return

    encrypted_password = cipher.encrypt(password.encode()).decode()

    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        data[service].append({"username": username, "password": encrypted_password})
    else:
        data[service] = [{"username": username, "password": encrypted_password}]

    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Kata sandi untuk '{service}' telah disimpan.")


def get_password(service):
    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)
    if service in data:
        print(f"\n🔐 Akun-akun untuk '{service}':")
        for i, account in enumerate(data[service], start=1):
            encrypted_password = account["password"]
            decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
            print(f"{i}. Username: {account['username']}, Password: {decrypted_password}")
    else:
        print("❌ Data tidak ditemukan!")


def update_password(service, username):
    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        for account in data[service]:
            if account["username"] == username:
                old_password_input = input("Masukkan password lama: ")
                encrypted_old_password = account["password"]
                decrypted_old_password = cipher.decrypt(encrypted_old_password.encode()).decode()

                if old_password_input == decrypted_old_password:
                    new_password = input("Masukkan password baru: ")

                    if not validate_password(new_password):  # Validasi kata sandi baru
                        return

                    account["password"] = cipher.encrypt(new_password.encode()).decode()

                    with open(FILE_NAME, "w") as f:
                        json.dump(data, f, indent=4)

                    print("✅ Password berhasil diperbarui!")
                    return
                else:
                    print("❌ Password lama tidak cocok.")
                    return
        print("❌ Username tidak ditemukan!")
    else:
        print("❌ Layanan tidak ditemukan!")


def delete_account(service, username):
    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        data[service] = [account for account in data[service] if account["username"] != username]
        if not data[service]:
            del data[service]

        with open(FILE_NAME, "w") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Akun '{username}' dari layanan '{service}' telah dihapus!")
    else:
        print("❌ Layanan tidak ditemukan!")


while True:
    print("\n======= Password Manager =======")
    print("1. Simpan kata sandi")
    print("2. Ambil kata sandi")
    print("3. Update kata sandi")
    print("4. Hapus Akun")
    print("0. Keluar")

    pilih = input("Masukkan pilihan: ").strip()

    if not pilih.isdigit():
        print("❌ Harap masukkan angka yang valid")
        continue

    pilih = int(pilih)

    if pilih == 1:
        service = input("Masukkan nama layanan: ")
        username = input("Masukkan username/email: ")
        password = input("Masukkan kata sandi: ")
        save_password(service, username, password)
    elif pilih == 2:
        service = input("Masukkan nama layanan: ")
        get_password(service)
    elif pilih == 3:
        service = input("Masukkan nama layanan: ")
        username = input("Masukkan username yang ingin diperbarui: ")
        update_password(service, username)
    elif pilih == 4:
        service = input("Masukkan nama layanan: ")
        username = input("Masukkan username yang ingin dihapus: ")
        delete_account(service, username)
    elif pilih == 0:
        print("🚀 Terima kasih telah menggunakan Password Manager!")
        break
    else:
        print("❌ Pilihan tidak valid. Coba lagi.")
