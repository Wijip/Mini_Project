import json
import os
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


def save_password():
    clear_window()
    tk.Label(root, text="Simpan Kata Sandi", font=("Arial", 14)).pack(pady=10)

    global service_entry, username_entry, password_entry

    tk.Label(root, text="Nama Layanan:").pack()
    service_entry = tk.Entry(root, width=30)
    service_entry.pack()

    tk.Label(root, text="Username/Email:").pack()
    username_entry = tk.Entry(root, width=30)
    username_entry.pack()

    tk.Label(root, text="Password:").pack()
    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.pack()

    tk.Button(root, text="Simpan", command=process_save_password).pack(pady=5)
    tk.Button(root, text="Kembali ke Menu", command=main_menu).pack(pady=5)


def process_save_password():
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if not service or not username or not password:
        messagebox.showerror("Error", "❌ Semua kolom harus diisi!")
        return

    ensure_file()
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
    main_menu()


def get_password():
    clear_window()
    tk.Label(root, text="Ambil Kata Sandi", font=("Arial", 14)).pack(pady=10)

    global service_entry
    tk.Label(root, text="Nama Layanan:").pack()
    service_entry = tk.Entry(root, width=30)
    service_entry.pack()

    tk.Button(root, text="Ambil", command=process_get_password).pack(pady=5)
    tk.Button(root, text="Kembali ke Menu", command=main_menu).pack(pady=5)


def process_get_password():
    service = service_entry.get()
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


def update_password():
    clear_window()
    tk.Label(root, text="Update Kata Sandi", font=("Arial", 14)).pack(pady=10)

    global service_entry, username_entry, new_password_entry
    tk.Label(root, text="Nama Layanan:").pack()
    service_entry = tk.Entry(root, width=30)
    service_entry.pack()

    tk.Label(root, text="Username/Email:").pack()
    username_entry = tk.Entry(root, width=30)
    username_entry.pack()

    tk.Label(root, text="Password Baru:").pack()
    new_password_entry = tk.Entry(root, width=30, show="*")
    new_password_entry.pack()

    tk.Button(root, text="Update", command=process_update_password).pack(pady=5)
    tk.Button(root, text="Kembali ke Menu", command=main_menu).pack(pady=5)


def process_update_password():
    service = service_entry.get()
    username = username_entry.get()
    new_password = new_password_entry.get()

    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        for account in data[service]:
            if account["username"] == username:
                account["password"] = cipher.encrypt(new_password.encode()).decode()

                with open(FILE_NAME, "w") as f:
                    json.dump(data, f, indent=4)

                messagebox.showinfo("Berhasil", "✅ Password berhasil diperbarui")
                main_menu()
                return
        messagebox.showerror("Error", "❌ Username tidak ditemukan!")
    else:
        messagebox.showerror("Error", "❌ Layanan tidak ditemukan!")


def delete_account():
    clear_window()
    tk.Label(root, text="Hapus Akun", font=("Arial", 14)).pack(pady=10)

    global service_entry, username_entry
    tk.Label(root, text="Nama Layanan:").pack()
    service_entry = tk.Entry(root, width=30)
    service_entry.pack()

    tk.Label(root, text="Username/Email:").pack()
    username_entry = tk.Entry(root, width=30)
    username_entry.pack()

    tk.Button(root, text="Hapus", command=process_delete_account).pack(pady=5)
    tk.Button(root, text="Kembali ke Menu", command=main_menu).pack(pady=5)


def process_delete_account():
    service = service_entry.get()
    username = username_entry.get()

    ensure_file()
    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    if service in data:
        data[service] = [account for account in data[service] if account["username"] != username]
        if not data[service]:
            del data[service]
        with open(FILE_NAME, "w") as f:
            json.dump(data, f, indent=4)

        messagebox.showinfo("Berhasil", f"✅ Akun '{username}' dari layanan '{service}' telah dihapus!")
    else:
        messagebox.showerror("Error", "❌ Layanan tidak ditemukan!")

    main_menu()


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def main_menu():
    clear_window()
    tk.Label(root, text="Password Manager", font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Simpan Kata Sandi", command=save_password).pack(pady=5)
    tk.Button(root, text="Ambil Kata Sandi", command=get_password).pack(pady=5)
    tk.Button(root, text="Update Kata Sandi", command=update_password).pack(pady=5)
    tk.Button(root, text="Hapus Akun", command=delete_account).pack(pady=5)
    tk.Button(root, text="Keluar", command=root.quit).pack(pady=20)


root = tk.Tk()
root.title("Password Manager")
root.geometry("400x400")

main_menu()
root.mainloop()
