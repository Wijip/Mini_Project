# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from converter import ImageConverter
import os

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter (PNG → WebP)")
        self.set_window_center(1366, 768)   # ukuran fix + auto center
        self.root.resizable(False, False)   # nonaktifkan resize

        self.converter = ImageConverter()

        # Header
        header = tk.Label(root, text="Image Converter", font=("Arial", 18, "bold"))
        header.pack(pady=8)

        # Search frame (atas)
        search_frame = tk.Frame(root)
        search_frame.pack(fill="x", padx=12, pady=6)

        tk.Label(search_frame, text="🔍 Cari File:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side="left", padx=6)
        btn_search = tk.Button(search_frame, text="Cari", command=self.search_file)
        btn_search.pack(side="left", padx=4)
        btn_reset = tk.Button(search_frame, text="Reset", command=self.refresh_list)
        btn_reset.pack(side="left", padx=4)

        # Main frame (grid) - kiri: daftar, kanan: aksi
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=12, pady=6)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=3)   # kiri (tree)
        main_frame.columnconfigure(1, weight=1)   # kanan (buttons)
        main_frame.rowconfigure(0, weight=1)

        # Left frame: Treeview
        left_frame = tk.LabelFrame(main_frame, text="Daftar File", padx=6, pady=6)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,8), pady=2)

        columns = ("No", "Nama File", "Ukuran", "Path", "Status")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)

        # Scrollbars
        scroll_y = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(left_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Heading kolom
        for col in columns:
            self.tree.heading(col, text=col)

        # Kolom
        self.tree.column("No", width=60, anchor="center", stretch=False)
        self.tree.column("Nama File", width=300, anchor="w", stretch=True)
        self.tree.column("Ukuran", width=140, anchor="center", stretch=False)
        self.tree.column("Path", width=700, anchor="w", stretch=True)
        self.tree.column("Status", width=140, anchor="center", stretch=False)

        # Layout tree + scrollbars di left_frame menggunakan grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew", columnspan=2)
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        # Right frame: Buttons
        right_frame = tk.LabelFrame(main_frame, text="Aksi", padx=8, pady=8)
        right_frame.grid(row=0, column=1, sticky="n", pady=2)

        # Tombol utama
        btn_refresh = tk.Button(right_frame, text="🔄 Refresh List", width=28, command=self.refresh_list)
        btn_refresh.pack(pady=6)

        btn_convert_selected = tk.Button(right_frame, text="✅ Konversi File Terpilih", width=28, command=self.convert_selected)
        btn_convert_selected.pack(pady=6)

        btn_batch = tk.Button(right_frame, text="⚙️ Konversi Semua", width=28, command=self.convert_batch)
        btn_batch.pack(pady=6)

        # Filter hasil
        btn_show_success = tk.Button(right_frame, text="📂 Lihat List Berhasil", width=28, command=self.show_success)
        btn_show_success.pack(pady=6)

        btn_show_fail = tk.Button(right_frame, text="📂 Lihat List Gagal", width=28, command=self.show_fail)
        btn_show_fail.pack(pady=6)

        btn_show_all = tk.Button(right_frame, text="📂 Kembali ke Semua File", width=28, command=self.refresh_list)
        btn_show_all.pack(pady=6)

        # Close button
        btn_close = tk.Button(right_frame, text="❌ Tutup Program", width=28, command=self.on_close)
        btn_close.pack(pady=(18,6))

        # Progress bar + label persentase (di bawah)
        progress_frame = tk.Frame(root)
        progress_frame.pack(fill="x", padx=12, pady=(6,10))
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=1100, mode="determinate")
        self.progress.pack(side="left", padx=(0,8), fill="x", expand=True)
        self.progress_label = tk.Label(progress_frame, text="0%")
        self.progress_label.pack(side="left")

        # Status bar
        self.status = tk.Label(root, text="Ready", anchor="w")
        self.status.pack(fill="x", padx=12, pady=(0,8))

        # Mode view: "all", "success", "fail", "search"
        self.view_mode = "all"
        self.search_keyword = ""

        # Load awal
        self.refresh_list()

    def set_window_center(self, width, height):
        """Atur window ke tengah layar dengan ukuran fix"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def refresh_list(self):
        """Tampilkan semua file dari folder input dengan status 'Belum'"""
        self.view_mode = "all"
        self.search_keyword = ""
        self._populate_from_input()
        self.status.config(text=f"{len(self.tree.get_children())} file ditemukan di folder input")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

    def _populate_from_input(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        files = [f for f in os.listdir(self.converter.input_dir) if f.lower().endswith(".png")]
        for i, filename in enumerate(sorted(files), start=1):
            file_path = os.path.join(self.converter.input_dir, filename)
            size_kb = max(1, os.path.getsize(file_path) // 1024)
            self.tree.insert("", "end", values=(i, filename, size_kb, file_path, "Belum"))

    def update_status(self, filename, status_text):
        """Update kolom Status pada Treeview jika file ada di tampilan saat ini"""
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if values[1] == filename:
                self.tree.item(item, values=(values[0], values[1], values[2], values[3], status_text))
                break

    def convert_selected(self):
        """Konversi file yang dipilih (hanya jika ada di folder input)"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih file terlebih dahulu.")
            return
        item = self.tree.item(selected[0])
        filename = item["values"][1]
        input_path = os.path.join(self.converter.input_dir, filename)

        if not os.path.exists(input_path):
            messagebox.showinfo("Info", "File tidak ditemukan di folder input. Mungkin sudah dipindahkan.")
            return

        success, info = self.converter.convert_file(input_path)
        if success:
            messagebox.showinfo("Sukses", f"File berhasil dikonversi ke:\n{info}")
            self.update_status(filename, "Berhasil")
            self.status.config(text=f"{filename} berhasil dikonversi")
        else:
            messagebox.showerror("Gagal", f"Konversi gagal: {info}")
            self.update_status(filename, "Gagal")
            self.status.config(text=f"{filename} gagal dikonversi")
        # refresh view sesuai mode saat ini
        if self.view_mode == "all":
            self._populate_from_input()
        elif self.view_mode == "search":
            self.search_file()

    def convert_batch(self):
        """Konversi semua file di folder input dengan update progress dan status kolom"""
        files = [f for f in os.listdir(self.converter.input_dir) if f.lower().endswith(".png")]
        files = sorted(files)
        total = len(files)
        if total == 0:
            messagebox.showinfo("Info", "Tidak ada file PNG di folder input.")
            return

        self.progress["maximum"] = total
        self.progress["value"] = 0
        self.progress_label.config(text="0%")
        sukses, gagal = 0, 0

        if self.view_mode != "all":
            self._populate_from_input()
            self.view_mode = "all"

        for i, filename in enumerate(files, start=1):
            input_path = os.path.join(self.converter.input_dir, filename)
            try:
                success, _ = self.converter.convert_file(input_path)
            except Exception:
                success = False

            if success:
                sukses += 1
                self.update_status(filename, "Berhasil")
            else:
                gagal += 1
                self.update_status(filename, "Gagal")

            self.progress["value"] = i
            percent = int((i / total) * 100)
            self.progress_label.config(text=f"{percent}%")
            self.root.update_idletasks()

        messagebox.showinfo("Hasil Batch", f"Berhasil: {sukses}\nGagal: {gagal}")
        self.status.config(text=f"Batch selesai: {sukses} berhasil, {gagal} gagal")
        self._populate_from_input()

    def show_success(self):
        """Tampilkan file yang ada di folder success"""
        self.view_mode = "success"
        self._filter_by_status_folder(self.converter.success_dir, "Berhasil")

    def show_fail(self):
        """Tampilkan file yang ada di folder fail"""
        self.view_mode = "fail"
        self._filter_by_status_folder(self.converter.fail_dir, "Gagal")

    def _filter_by_status_folder(self, folder, status_label):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
        for i, filename in enumerate(sorted(files), start=1):
            file_path = os.path.join(folder, filename)
            size_kb = max(1, os.path.getsize(file_path) // 1024)
            self.tree.insert("", "end", values=(i, filename, size_kb, file_path, status_label))

        self.status.config(text=f"Menampilkan {len(files)} file dengan status {status_label}")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

    def search_file(self):
        """Cari file di folder input berdasarkan keyword (substring, case-insensitive)"""
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            messagebox.showinfo("Info", "Masukkan kata kunci pencarian.")
            return

        self.view_mode = "search"
        self.search_keyword = keyword

        for item in self.tree.get_children():
            self.tree.delete(item)

        files = [f for f in os.listdir(self.converter.input_dir) if f.lower().endswith(".png")]
        matched = [f for f in files if keyword in f.lower()]
        for i, filename in enumerate(sorted(matched), start=1):
            file_path = os.path.join(self.converter.input_dir, filename)
            size_kb = max(1, os.path.getsize(file_path) // 1024)
            self.tree.insert("", "end", values=(i, filename, size_kb, file_path, "Belum"))

        self.status.config(text=f"{len(matched)} hasil pencarian untuk '{self.search_var.get()}'")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

    def on_close(self):
        """Konfirmasi sebelum menutup aplikasi"""
        if messagebox.askokcancel("Keluar", "Tutup program?"):
            self.root.quit()
