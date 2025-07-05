import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


FILE_TAMBAH     = "tambah.txt"
FILE_SELESAI    = "selesai.txt"
FILE_LOG        = "log.txt"

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_action(action, name, program):
    with open(FILE_LOG, "a") as f:
        f.write(f"{timestamp()} | {action.upper():7} | {name} | {program}\n")

class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Tambah Murid")
        self.resizable(False, False)
        self.result = None

        tk.Label(self, text="Nama murid:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ent_name = tk.Entry(self, width=30)
        self.ent_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Program:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_prog = tk.Entry(self, width=30)
        self.ent_prog.grid(row=1, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK", width=10, command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Batal", width=10, command=self.destroy).pack(side="right", padx=5)

        self.transient(parent)
        self.grab_set()
        self.ent_name.focus_set()

    def on_ok(self):
        name = self.ent_name.get().strip()
        prog = self.ent_prog.get().strip()
        if not name or not prog:
            messagebox.showerror("Error Input", "Nama dan Program wajib diisi.", parent=self)
            return
        self.result = (name, prog)
        self.destroy()

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.tasks = []

        self._build_ui()
        self._load_tasks()

    def _build_ui(self):
        self.container = tk.Frame(self.root)
        self.container.pack(padx=10, pady=10, fill="x")

        hdr = tk.Frame(self.container)
        hdr.pack(fill="x")
        tk.Label(hdr, text="", width=4).grid(row=0, column=0)
        tk.Label(hdr, text="Nama", width=20).grid(row=0, column=1)
        tk.Label(hdr, text="Program", width=20).grid(row=0, column=2)
        tk.Label(hdr, text="Waktu Tambah", width=20).grid(row=0, column=3)
        tk.Label(hdr, text="Action", width=20).grid(row=0, column=4)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=(0,10))
        tk.Button(btn_frame, text="Tambah",         command=self.add_task_dialog).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Lihat Selesai",  command=self.show_completed).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Exit",           command=self.root.quit).grid(row=0, column=2, padx=5)

    def _load_tasks(self):
        if not os.path.exists(FILE_TAMBAH):
            return
        with open(FILE_TAMBAH) as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) == 3:
                    ts, name, prog = parts
                    self._create_task_row(name, prog, ts, save=False)

    def _save_all_tasks(self):
        with open(FILE_TAMBAH, "w") as f:
            for t in self.tasks:
                f.write(f"{t['ts']} | {t['name']} | {t['prog']}\n")

    def add_task_dialog(self):
        dlg = AddTaskDialog(self.root)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        name, prog = dlg.result
        ts = timestamp()
        self._create_task_row(name, prog, ts, save=True)
        messagebox.showinfo("Sukses", "Data ditambahkan.", parent=self.root)

    def _create_task_row(self, name, prog, ts, save):
        row = tk.Frame(self.container)
        row.pack(fill="x", pady=2)

        var = tk.BooleanVar()
        chk = tk.Checkbutton(row, variable=var, command=lambda v=var, r=row: self.complete_task(v,r))
        chk.grid(row=0, column=0)

        lbl_name = tk.Label(row, text=name, width=20, anchor="w"); lbl_name.grid(row=0, column=1)
        lbl_prog = tk.Label(row, text=prog, width=20, anchor="w"); lbl_prog.grid(row=0, column=2)
        lbl_ts   = tk.Label(row, text=ts,   width=20, anchor="w"); lbl_ts.grid(row=0, column=3)

        btn_edit = tk.Button(row, text="Edit", command=lambda r=row: self.edit_task(r))
        btn_edit.grid(row=0, column=4, padx=2)
        btn_del  = tk.Button(row, text="Hapus", command=lambda r=row: self.delete_task(r))
        btn_del.grid(row=0, column=5, padx=2)

        self.tasks.append({
            "frame":row, "var": var,
            "name": name, "prog": prog, "ts": ts,
            "widgets": (lbl_name, lbl_prog, lbl_ts)
        })

        if save:
            with open(FILE_TAMBAH, "a") as f:
                f.write(f"{ts} | {name} | {prog}\n")
            log_action("tambah", name, prog)

    def _find_task(self, frame):
        for t in self.tasks:
            if t["frame"] == frame:
                return t
        return None

    def complete_task(self, var, frame):
        if not var.get():
            return
        t = self._find_task(frame)
        if not t:
            return
        with open(FILE_SELESAI, "a") as f:
            f.write(f"{t['ts']} | {t['name']} | {t['prog']}\n")
        log_action("Selesai", t["name"], t["prog"])
        frame.destroy()
        self.tasks.remove(t)
        self._save_all_tasks()

    def delete_task(self, frame):
        t = self._find_task(frame)
        if not t:
            return
        if messagebox.askyesno("Konfirmasi", "Hapus data ini?", parent=self.root):
            log_action("Hapus", t["name"], t["prog"])
            frame.destroy()
            self.tasks.remove(t)
            self._save_all_tasks()

    def edit_task(self, frame):
        t = self._find_task(frame)
        if not t:
            return
        dlg = AddTaskDialog(self.root)
        dlg.ent_name.insert(0, t["name"])
        dlg.ent_prog.insert(0, t["prog"])
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        new_name, new_prog = dlg.result
        old = (t["name"], t["prog"])
        t["name"], t["prog"] = new_name, new_prog
        t["widgets"][0].config(text=new_name)
        t["widgets"][1].config(text=new_prog)
        log_action("edit", f"{old[0]} -> {new_name}", f"{old[1]} -> {new_prog}")
        self._save_all_tasks()

    def show_completed(self):
        if not os.path.exists(FILE_SELESAI):
            messagebox.showinfo("Selesai", "Belum ada data selesai.", perent=self.root)
            return
        win = tk.Toplevel(self.root)
        win.title("Data Selesai")
        txt = tk.Text(win, width=60, height=20, bg="#f0f0f0")
        txt.pack(padx=10, pady=10)
        with open(FILE_SELESAI) as f:
            txt.insert("1.0", f.read().strip() or "Tidak ada data.")
        txt.config(state="disabled")

if __name__ == '__main__':
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()