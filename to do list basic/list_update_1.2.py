import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime

FILE_TAMBAH   = "tambah.txt"
FILE_SELESAI  = "selesai.txt"
FILE_LOG      = "log.txt"

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_action(action, name, program):
    with open(FILE_LOG, "a") as f:
        f.write(f"{timestamp()} | {action.upper():7} | {name} | {program}\n")

class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, name="", prog=""):
        super().__init__(parent)
        self.title("Tambah / Edit Murid")
        self.resizable(False, False)
        self.result = None

        tk.Label(self, text="Nama murid:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ent_name = tk.Entry(self, width=30)
        self.ent_name.grid(row=0, column=1, padx=10, pady=5)
        self.ent_name.insert(0, name)

        tk.Label(self, text="Program:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_prog = tk.Entry(self, width=30)
        self.ent_prog.grid(row=1, column=1, padx=10, pady=5)
        self.ent_prog.insert(0, prog)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK",   width=10, command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Batal",width=10, command=self.destroy).pack(side="right", padx=5)

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
        self.root.title("To-Do List Murid")
        self.per_page = 10
        self.current_page = 0
        self.tasks_data = []  # list of dicts: {name,prog,ts}

        self._load_data()
        self._build_ui()
        self._display_tasks()

    def _load_data(self):
        if not os.path.exists(FILE_TAMBAH):
            return
        with open(FILE_TAMBAH) as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) == 3:
                    ts, name, prog = parts
                    self.tasks_data.append({"name": name, "prog": prog, "ts": ts})

    def _save_all(self):
        with open(FILE_TAMBAH, "w") as f:
            for t in self.tasks_data:
                f.write(f"{t['ts']} | {t['name']} | {t['prog']}\n")

    def _build_ui(self):
        # Header
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(fill="x", padx=10, pady=(10,0))
        tk.Label(self.header_frame, text="",            width=4).grid(row=0, column=0)
        tk.Label(self.header_frame, text="Nama",        width=20).grid(row=0, column=1)
        tk.Label(self.header_frame, text="Program",     width=20).grid(row=0, column=2)
        tk.Label(self.header_frame, text="Waktu Tambah",width=20).grid(row=0, column=3)
        tk.Label(self.header_frame, text="Action",      width=20).grid(row=0, column=4)

        # Rows container
        self.rows_frame = tk.Frame(self.root)
        self.rows_frame.pack(fill="x", padx=10)

        # Control buttons
        ctrl = tk.Frame(self.root)
        ctrl.pack(pady=(10,5))
        tk.Button(ctrl, text="Tambah",        command=self._on_add).grid(row=0, column=0, padx=5)
        tk.Button(ctrl, text="Lihat Selesai", command=self._show_completed).grid(row=0, column=1, padx=5)
        tk.Button(ctrl, text="Exit",          command=self.root.quit).grid(row=0, column=2, padx=5)

        # Pagination buttons
        pag = tk.Frame(self.root)
        pag.pack(pady=(0,10))
        self.prev_btn = tk.Button(pag, text="<< Prev", command=self._prev_page)
        self.prev_btn.grid(row=0, column=0, padx=5)
        self.page_lbl = tk.Label(pag, text="")
        self.page_lbl.grid(row=0, column=1, padx=5)
        self.next_btn = tk.Button(pag, text="Next >>", command=self._next_page)
        self.next_btn.grid(row=0, column=2, padx=5)

    def _display_tasks(self):
        # Clear old rows
        for w in self.rows_frame.winfo_children():
            w.destroy()

        total = len(self.tasks_data)
        pages = (total - 1) // self.per_page + 1
        self.current_page = max(0, min(self.current_page, pages - 1))
        start = self.current_page * self.per_page
        end   = start + self.per_page

        # Update page label & button states
        self.page_lbl.config(text=f"Page {self.current_page+1} / {pages}")
        self.prev_btn.config(state="normal" if self.current_page>0 else "disabled")
        self.next_btn.config(state="normal" if self.current_page<pages-1 else "disabled")

        # Render rows for this page
        for idx, t in enumerate(self.tasks_data[start:end], start):
            row = tk.Frame(self.rows_frame)
            row.pack(fill="x", pady=2)

            var = tk.BooleanVar()
            chk = tk.Checkbutton(row, variable=var,
                                 command=lambda v=var, i=idx: self._complete(i))
            chk.grid(row=0, column=0)

            tk.Label(row, text=t["name"], width=20, anchor="w").grid(row=0, column=1)
            tk.Label(row, text=t["prog"], width=20, anchor="w").grid(row=0, column=2)
            tk.Label(row, text=t["ts"],   width=20, anchor="w").grid(row=0, column=3)

            tk.Button(row, text="Edit",  command=lambda i=idx: self._edit(i)).grid(row=0, column=4, padx=2)
            tk.Button(row, text="Hapus", command=lambda i=idx: self._delete(i)).grid(row=0, column=5, padx=2)

    def _on_add(self):
        dlg = AddTaskDialog(self.root)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        name, prog = dlg.result
        ts = timestamp()
        self.tasks_data.append({"name": name, "prog": prog, "ts": ts})
        log_action("tambah", name, prog)
        self._save_all()
        # Jump to last page
        self.current_page = (len(self.tasks_data)-1)//self.per_page
        self._display_tasks()

    def _complete(self, index):
        t = self.tasks_data[index]
        with open(FILE_SELESAI, "a") as f:
            f.write(f"{t['ts']} | {t['name']} | {t['prog']}\n")
        log_action("selesai", t["name"], t["prog"])
        del self.tasks_data[index]
        self._save_all()
        self._display_tasks()

    def _delete(self, index):
        t = self.tasks_data[index]
        if messagebox.askyesno("Konfirmasi", "Hapus data ini?", parent=self.root):
            log_action("hapus", t["name"], t["prog"])
            del self.tasks_data[index]
            self._save_all()
            self._display_tasks()

    def _edit(self, index):
        t = self.tasks_data[index]
        dlg = AddTaskDialog(self.root, t["name"], t["prog"])
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        new_name, new_prog = dlg.result
        log_action("edit",
                   f"{t['name']}→{new_name}",
                   f"{t['prog']}→{new_prog}")
        t["name"], t["prog"] = new_name, new_prog
        self._save_all()
        self._display_tasks()

    def _show_completed(self):
        if not os.path.exists(FILE_SELESAI):
            messagebox.showinfo("Selesai", "Belum ada data selesai.", parent=self.root)
            return
        win = tk.Toplevel(self.root)
        win.title("Data Selesai")
        txt = tk.Text(win, width=60, height=20, bg="#f0f0f0")
        txt.pack(padx=10, pady=10)
        with open(FILE_SELESAI) as f:
            txt.insert("1.0", f.read().strip() or "Tidak ada data.")
        txt.config(state="disabled")

    def _prev_page(self):
        self.current_page -= 1
        self._display_tasks()

    def _next_page(self):
        self.current_page += 1
        self._display_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
