import os
import shutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# ========= Konfigurasi dasar =========
FILE_TAMBAH   = "tambah.txt"
FILE_SELESAI  = "selesai.txt"
FILE_LOG      = "log.txt"
DATEFMT       = "%Y-%m-%d %H:%M:%S"

# Folder untuk integrasi upload
UPLOAD_DIR    = "upload_video"
SELESAI_DIR   = "selesai_upload"
VIDEO_EXTS    = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm", ".m4v")

# ========= Util umum =========
def timestamp():
    return datetime.now().strftime(DATEFMT)

def log_action(action, name, program):
    with open(FILE_LOG, "a") as f:
        f.write(f"{timestamp()} | {action.upper():7} | {name} | {program}\n")

class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, name="", prog="", dl=""):
        super().__init__(parent)
        self.title("Tambah / Edit Murid")
        self.resizable(False, False)
        self.result = None

        tk.Label(self, text="Nama murid:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ent_name = tk.Entry(self, width=30)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)
        self.ent_name.insert(0, name)

        tk.Label(self, text="Program:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ent_prog = tk.Entry(self, width=30)
        self.ent_prog.grid(row=1, column=1, padx=5, pady=5)
        self.ent_prog.insert(0, prog)

        tk.Label(self, text="Deadline (YYYY-MM-DD HH:MM:SS):").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.ent_deadline = tk.Entry(self, width=30)
        self.ent_deadline.grid(row=2, column=1, padx=5, pady=5)
        self.ent_deadline.insert(0, dl)

        btnf = tk.Frame(self)
        btnf.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(btnf, text="OK",   width=10, command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btnf, text="Batal",width=10, command=self.destroy).pack(side="right", padx=5)

        self.transient(parent)
        self.grab_set()
        self.ent_name.focus_set()

    def on_ok(self):
        name = self.ent_name.get().strip()
        prog = self.ent_prog.get().strip()
        dl_str = self.ent_deadline.get().strip()
        if not name or not prog or not dl_str:
            messagebox.showerror("Error Input", "Semua field wajib diisi.", parent=self)
            return
        try:
            datetime.strptime(dl_str, DATEFMT)
        except ValueError:
            messagebox.showerror("Error Input", "Format deadline salah.", parent=self)
            return
        self.result = (name, prog, dl_str)
        self.destroy()

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Murid dengan Deadline + Upload Integrasi")
        self.per_page = 10
        self.current_page = 0
        self.tasks_data = []  # {name, prog, ts, dl, countdown_lbl?}

        self._ensure_dirs()
        self._load_data()
        self._build_ui()
        self._refresh_display()
        self._schedule_countdown()
        self._schedule_scan_uploads()

    # ====== File & folder handling ======
    def _ensure_dirs(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(SELESAI_DIR, exist_ok=True)

    def _load_data(self):
        if not os.path.exists(FILE_TAMBAH):
            return
        with open(FILE_TAMBAH) as f:
            for line in f:
                parts = line.strip().split(" | ")
                # format: ts | name | prog | dl
                if len(parts) == 4:
                    ts, name, prog, dl = parts
                    self.tasks_data.append({
                        "name": name, "prog": prog,
                        "ts": ts,   "dl": dl
                    })

    def _save_all(self):
        with open(FILE_TAMBAH, "w") as f:
            for t in self.tasks_data:
                f.write(f"{t['ts']} | {t['name']} | {t['prog']} | {t['dl']}\n")

    # ====== UI ======
    def _build_ui(self):
        hdr = tk.Frame(self.root)
        hdr.pack(fill="x", padx=10, pady=(10,0))
        tk.Label(hdr, text="",            width=4).grid(row=0,column=0)
        tk.Label(hdr, text="Nama",        width=25, anchor="w").grid(row=0,column=1, sticky="w")
        tk.Label(hdr, text="Program",     width=18, anchor="w").grid(row=0,column=2, sticky="w")
        tk.Label(hdr, text="Deadline",    width=20, anchor="w").grid(row=0,column=3, sticky="w")
        tk.Label(hdr, text="Sisa Waktu",  width=15, anchor="w").grid(row=0,column=4, sticky="w")
        tk.Label(hdr, text="Action",      width=15, anchor="w").grid(row=0,column=5, sticky="w")

        self.rows_frame = tk.Frame(self.root)
        self.rows_frame.pack(fill="x", padx=10, pady=5)

        cf = tk.Frame(self.root)
        cf.pack(pady=(0,5))
        tk.Button(cf, text="Tambah",        command=self._on_add).grid(row=0,column=0,padx=5)
        tk.Button(cf, text="Lihat Selesai", command=self._show_completed).grid(row=0,column=1,padx=5)
        tk.Button(cf, text="Exit",          command=self.root.quit).grid(row=0,column=2,padx=5)

        pf = tk.Frame(self.root)
        pf.pack(pady=(5,10))
        self.prev_btn = tk.Button(pf, text="<< Prev", command=self._prev_page)
        self.prev_btn.grid(row=0,column=0,padx=5)
        self.page_lbl = tk.Label(pf, text="")
        self.page_lbl.grid(row=0,column=1,padx=5)
        self.next_btn = tk.Button(pf, text="Next >>", command=self._next_page)
        self.next_btn.grid(row=0,column=2,padx=5)

    def _refresh_display(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()

        total = len(self.tasks_data)
        pages = max(1, (total-1)//self.per_page + 1)
        self.current_page = max(0, min(self.current_page, pages-1))
        start = self.current_page*self.per_page
        end   = start + self.per_page

        self.page_lbl.config(text=f"Page {self.current_page+1}/{pages}")
        self.prev_btn.config(state=("normal" if self.current_page>0 else "disabled"))
        self.next_btn.config(state=("normal" if self.current_page<pages-1 else "disabled"))

        for idx, t in enumerate(self.tasks_data[start:end], start=start):
            row = tk.Frame(self.rows_frame)
            row.pack(fill="x", pady=2)

            var = tk.BooleanVar()
            tk.Checkbutton(row, variable=var,
                command=lambda v=var,i=idx: self._complete(i)
            ).grid(row=0,column=0, padx=2)

            tk.Label(row, text=t["name"], width=25, anchor="w").grid(row=0,column=1, sticky="w")
            tk.Label(row, text=t["prog"],  width=18, anchor="w").grid(row=0,column=2, sticky="w")
            tk.Label(row, text=t["dl"],    width=20, anchor="w").grid(row=0,column=3, sticky="w")

            cd_lbl = tk.Label(row, text="", width=15)
            cd_lbl.grid(row=0, column=4, sticky="w")
            t["countdown_lbl"] = cd_lbl  # simpan reference

            tk.Button(row, text="Edit",  command=lambda i=idx: self._edit(i)).grid(row=0,column=5,padx=2)
            tk.Button(row, text="Hapus", command=lambda i=idx: self._delete(i)).grid(row=0,column=6,padx=2)

        self._update_countdowns_once()

    # ====== Countdown ======
    def _update_countdowns_once(self):
        now = datetime.now()
        for t in self.tasks_data:
            lbl = t.get("countdown_lbl")
            if not lbl:
                continue
            try:
                dl = datetime.strptime(t["dl"], DATEFMT)
            except ValueError:
                lbl.config(text="INVALID", fg="red")
                continue

            diff = dl - now
            if diff.total_seconds() <= 0:
                lbl.config(text="EXPIRED", fg="red")
            else:
                days    = diff.days
                hours   = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60
                seconds = diff.seconds % 60
                if days > 0:
                    time_str = f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
                else:
                    time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                lbl.config(text=time_str, fg="black")

    def _schedule_countdown(self):
        self._update_countdowns_once()
        self.root.after(1000, self._schedule_countdown)

    # ====== Event tombol ======
    def _on_add(self):
        dlg = AddTaskDialog(self.root)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        name, prog, dl = dlg.result
        ts = timestamp()
        self.tasks_data.append({"name":name,"prog":prog,"ts":ts,"dl":dl})
        log_action("tambah", name, prog)
        self._save_all()
        self.current_page = (len(self.tasks_data)-1)//self.per_page
        self._refresh_display()

    def _complete(self, idx):
        # Pindahkan ke selesai_upload jika ada di upload_video
        t = self.tasks_data[idx]
        src_path = os.path.join(UPLOAD_DIR, t["name"])
        if os.path.exists(src_path):
            dst_path = os.path.join(SELESAI_DIR, t["name"])
            # Jika tujuan sudah ada, tambahkan suffix timestamp agar unik
            if os.path.exists(dst_path):
                base = os.path.basename(t["name"])
                name, ext = os.path.splitext(base)
                suffix = datetime.now().strftime("%Y%m%d-%H%M%S")
                dst_path = os.path.join(SELESAI_DIR, f"{name}_{suffix}{ext}")
            try:
                shutil.move(src_path, dst_path)
            except Exception as e:
                messagebox.showwarning("Peringatan", f"Gagal memindahkan: {e}")

        with open(FILE_SELESAI, "a") as f:
            f.write(f"{t['ts']} | {t['name']} | {t['prog']} | {t['dl']}\n")
        log_action("selesai", t["name"], t["prog"])
        del self.tasks_data[idx]
        self._save_all()
        self._refresh_display()

    def _delete(self, idx):
        t = self.tasks_data[idx]
        if messagebox.askyesno("Konfirmasi", "Hapus data ini?", parent=self.root):
            log_action("hapus", t["name"], t["prog"])
            del self.tasks_data[idx]
            self._save_all()
            self._refresh_display()

    def _edit(self, idx):
        t = self.tasks_data[idx]
        dlg = AddTaskDialog(self.root, t["name"], t["prog"], t["dl"])
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        new_name, new_prog, new_dl = dlg.result
        log_action("edit",
                   f"{t['name']}→{new_name}",
                   f"{t['prog']}→{new_prog}")
        t["name"], t["prog"], t["dl"] = new_name, new_prog, new_dl
        self._save_all()
        self._refresh_display()

    def _show_completed(self):
        if not os.path.exists(FILE_SELESAI):
            messagebox.showinfo("Selesai", "Belum ada data selesai.", parent=self.root)
            return
        win = tk.Toplevel(self.root)
        win.title("Data Selesai")
        txt = tk.Text(win, width=80, height=20, bg="#f0f0f0")
        txt.pack(padx=10, pady=10)
        with open(FILE_SELESAI) as f:
            txt.insert("1.0", f.read().strip() or "Tidak ada data.")
        txt.config(state="disabled")

    def _prev_page(self):
        self.current_page -= 1
        self._refresh_display()

    def _next_page(self):
        self.current_page += 1
        self._refresh_display()

    # ====== Integrasi upload ======
    def _is_video_item(self, path):
        if os.path.isdir(path):
            return True
        name_lower = os.path.basename(path).lower()
        return name_lower.endswith(VIDEO_EXTS)

    def _scan_upload_folder_once(self):
        try:
            existing_names = {t["name"] for t in self.tasks_data}
            for item in os.listdir(UPLOAD_DIR):
                if item.startswith("~") or item.startswith("."):
                    continue
                path = os.path.join(UPLOAD_DIR, item)
                if self._is_video_item(path) and item not in existing_names:
                    # Tambah task otomatis untuk upload video
                    ts = timestamp()
                    dl = (datetime.now() + timedelta(days=7)).strftime(DATEFMT)
                    self.tasks_data.append({
                        "name": item,
                        "prog": "Upload Video",
                        "ts": ts,
                        "dl": dl
                    })
                    log_action("tambah", item, "Upload Video")
                    self._save_all()
                    # Agar user langsung lihat yang baru, lompat ke last page
                    self.current_page = (len(self.tasks_data)-1)//self.per_page
                    self._refresh_display()
        except FileNotFoundError:
            # Jika folder dihapus saat runtime, buat lagi
            self._ensure_dirs()

    def _schedule_scan_uploads(self, interval_ms=5000):
        self._scan_upload_folder_once()
        self.root.after(interval_ms, self._schedule_scan_uploads)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
