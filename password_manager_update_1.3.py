import json
import os
import re
import tkinter as tk
from tkinter import messagebox
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


def validate_password(password):
    if len(password) < 8:
        messagebox.showerror("Error", "❌ Kata sandi harus minimal 8 karakter.")
        return False
    if not re.search(r"[A-Z]", password):
        messagebox.showerror("Error", "❌ Kata sandi harus mengandung huruf besar.")
        return False
    if not re.search(r"[a-z]", password):
        messagebox.showerror("Error", "❌ Kata sandi harus mengandung huruf kecil.")
        return False
    if not re.search(r"\d", password):
        messagebox.showerror("Error", "❌ Kata sandi harus mengandung angka.")
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        messagebox.showerror("Error", "❌ Kata sandi harus mengandung simbol spesial.")
        return False
    return True


def save_password(service, username, password):
    ensure_file()
    if not validate_password(password):
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

    messagebox.showinfo("Berhasil", f"✅ Kata sandi untuk '{service}' telah disimpan.")


def get_password(service):
    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        result = "\n🔐 Akun untuk '{}':\n".format(service)
        for account in data[service]:
            encrypted_password = account["password"]
            decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
            result += f"Username: {account['username']}, Password: {decrypted_password}\n"

        messagebox.showinfo("Kata Sandi Ditemukan", result)
    else:
        messagebox.showerror("Error", "❌ Data tidak ditemukan!")


def update_password(service, username, old_password, new_password):
    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        for account in data[service]:
            if account["username"] == username:
                encrypted_old_password = account["password"]
                decrypted_old_password = cipher.decrypt(encrypted_old_password.encode()).decode()

                if old_password == decrypted_old_password:
                    if not validate_password(new_password):
                        return

                    account["password"] = cipher.encrypt(new_password.encode()).decode()

                    with open(FILE_NAME, "w") as f:
                        json.dump(data, f, indent=4)

                    messagebox.showinfo("Berhasil", "✅ Password berhasil diperbarui!")
                    return
                else:
                    messagebox.showerror("Error", "❌ Password lama tidak cocok.")
                    return
        messagebox.showerror("Error", "❌ Username tidak ditemukan!")
    else:
        messagebox.showerror("Error", "❌ Layanan tidak ditemukan!")


def delete_account(service, username):
    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        original_count = len(data[service])  # Hitung jumlah akun sebelum penghapusan
        data[service] = [account for account in data[service] if account["username"] != username]
        updated_count = len(data[service])  # Hitung jumlah akun setelah penghapusan

        if original_count == updated_count:
            messagebox.showerror("Error", f"❌ Username '{username}' tidak ditemukan dalam layanan '{service}'!")
            return
        if not data[service]:
            del data[service]

        with open(FILE_NAME, "w") as f:
            json.dump(data, f, indent=4)

        messagebox.showinfo("Berhasil", f"✅ Akun '{username}' dari layanan '{service}' telah dihapus!")
    else:
        messagebox.showerror("Error", f"❌ Layanan '{service}' tidak ditemukan!")



class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("400x400")
        self.main_menu()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_frame()
        tk.Label(self.root, text="Password Manager", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Simpan Kata Sandi", command=self.save_menu).pack(pady=5)
        tk.Button(self.root, text="Ambil Kata Sandi", command=self.get_menu).pack(pady=5)
        tk.Button(self.root, text="Update Kata Sandi", command=self.update_menu).pack(pady=5)
        tk.Button(self.root, text="Hapus Akun", command=self.delete_menu).pack(pady=5)
        tk.Button(self.root, text="Keluar", command=self.root.quit).pack(pady=20)

    def save_menu(self):
        self.clear_frame()
        tk.Label(self.root, text="Simpan Kata Sandi", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Masukkan Nama Service", font=("Arial", 12)).pack()
        service_entry = tk.Entry(self.root, width=30)
        service_entry.pack()
        tk.Label(self.root, text="Masukkan Email/Username", font=("Arial", 12)).pack()
        username_entry = tk.Entry(self.root, width=30)
        username_entry.pack()
        tk.Label(self.root, text="Masukkan Password", font=("Arial", 12)).pack()
        password_entry = tk.Entry(self.root, width=30, show="*")
        password_entry.pack()

        tk.Button(self.root, text="Simpan",
                  command=lambda: save_password(service_entry.get(), username_entry.get(), password_entry.get())).pack(
            pady=10)
        tk.Button(self.root, text="Kembali", command=self.main_menu).pack(pady=5)

    def get_menu(self):
        self.clear_frame()
        tk.Label(self.root, text="Ambil Kata Sandi", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Masukkan Nama Layanan", font=("Arial", 12)).pack()
        service_entry = tk.Entry(self.root, width=30)
        service_entry.pack()

        tk.Button(self.root, text="Ambil", command=lambda: get_password(service_entry.get())).pack(pady=10)
        tk.Button(self.root, text="Kembali", command=self.main_menu).pack(pady=5)

    def update_menu(self):
        self.clear_frame()
        tk.Label(self.root, text="Update Kata Sandi", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Masukkan Nama Layanan", font=("Arial", 12)).pack()
        service_entry = tk.Entry(self.root, width=30)
        service_entry.pack()
        tk.Label(self.root, text="Masukkan username", font=("Arial", 12)).pack()
        username_entry = tk.Entry(self.root, width=30)
        username_entry.pack()
        tk.Label(self.root, text="Masukkan Password Lama", font=("Arial", 12)).pack()
        old_password_entry = tk.Entry(self.root, width=30, show="*")
        old_password_entry.pack()
        tk.Label(self.root, text="Masukkan Password Baru", font=("Arial", 12)).pack()
        new_password_entry = tk.Entry(self.root, width=30, show="*")
        new_password_entry.pack()

        tk.Button(self.root, text="Update",
                  command=lambda: update_password(service_entry.get(), username_entry.get(), old_password_entry.get(),
                                                  new_password_entry.get())).pack(pady=10)
        tk.Button(self.root, text="Kembali", command=self.main_menu).pack(pady=5)

    def delete_menu(self):
        self.clear_frame()
        tk.Label(self.root, text="Hapus Akun", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Masukkan Nama Layanan", font=("Arial", 12)).pack()
        service_entry = tk.Entry(self.root, width=30)
        service_entry.pack()
        tk.Label(self.root, text="Masukkan username", font=("Arial", 12)).pack()
        username_entry = tk.Entry(self.root, width=30)
        username_entry.pack()

        tk.Button(self.root, text="Hapus",
                  command=lambda: delete_account(service_entry.get(), username_entry.get())).pack(pady=10)
        tk.Button(self.root, text="Kembali", command=self.main_menu).pack(pady=5)


# Jalankan Program
root = tk.Tk()
app = PasswordManagerApp(root)
root.mainloop()
