import tkinter as tk
from tkinter import messagebox

class Mahassiwa:
    def __init__(self, nama, nim, usia, juruan, alamat):
        self.nama = nama
        self.nim = nim
        self.usia = usia
        self.juruan = juruan
        self.alamat = alamat
        self.tahun_masuk = "20" + nim[:2]

    def simpan_data(self):
        return{
            "Nama": self.nama,
            "NIM": self.nim,
            "Tahun Masuk": self.tahun_masuk,
            "Usia": self.usia,
            "Juruan": self.juruan,
            "Alamat": self.alamat
        }

class MahasiswaForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Data Mahasiswa")
        self.root.geometry("400x450")
        self._create_widgets()

    def _create_widgets(self):
        frame_in = tk.Frame(self.root, pady=10)
        frame_in.pack(fill="x")
        labels = ["Nama", "NIM", "Usia", "Jurusan", "Alamat"]
        self.entries = {}
        for i, text in enumerate(labels):
            tk.Label(frame_in, text=text + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            ent = tk.Entry(frame_in, width=30)
            ent.grid(row=i, column=1, padx=5, pady=5)
            self.entries[text.lower()] = ent

        btn = tk.Button(
            self.root,
            text="Simpan & Tampilkan",
            width=20,
            command=self._on_submit
        )
        btn.pack(pady=10)

        self.output = tk.Text(self.root, height=10, width=45, state="disabled", bg="#f0f0f0")
        self.output.pack(padx=10, pady=10)

    def _on_submit(self):
        nama        = self.entries["nama"].get().strip()
        nim         = self.entries["nim"].get().strip()
        usia        = self.entries["usia"].get().strip()
        juruan      = self.entries["jurusan"].get().strip()
        alamat      = self.entries["alamat"].get().strip()

        if not(nama and nim and usia and juruan and alamat):
            messagebox.showerror("Error Input", "Semua field wajib diisi.")
            return
        if not (nim.isdigit() and usia.isdigit()):
            messagebox.showerror("Error Input", "NIM dan usia harus berupa angka.")
            return

        mhs = Mahassiwa(nama, nim, usia, juruan, alamat)
        data = mhs.simpan_data()

        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)

        self.output.insert(tk.END, "=== Data Mahasiswa ===\n\n")
        for key, val in data.items():
            self.output.insert(tk.END, f"{key:16}: {val}\n")
        self.output.insert(tk.END, "\nTerimakasih sudah menggunakan sistem ini.")
        self.output.config(state="disabled")

if __name__ == '__main__':
    root = tk.Tk()
    app = MahasiswaForm(root)
    root.mainloop()