import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

MENU_FILE = "menu.json"
PESANAN_FILE = "pesanan.txt"
LOG_FILE = "log.txt"


# ---------- Utilitas umum ----------
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_action(action, detail=""):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now_str()} | {action.upper():12} | {detail}\n")


def load_menu():
    if not os.path.exists(MENU_FILE):
        sample = {
            "Dimsum Goreng": {
                "harga": 15000,
                "opsi": {
                    "Chili Oil": 2000,
                    "Saus Bangkok": 1500
                }
            },
            "Nasi Goreng Spesial": {
                "harga": 20000,
                "opsi": {}
            }
        }
        save_menu(sample)
        return sample
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_menu(menu):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu, f, indent=2, ensure_ascii=False)


def center_window(win, parent):
    """
    Posisikan window 'win' di tengah 'parent'.
    Jika ukuran parent belum tersedia, fallback ke tengah layar.
    """
    win.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()

    ww = win.winfo_width()
    wh = win.winfo_height()

    if pw <= 1 and ph <= 1:
        # fallback: center on screen
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - ww) // 2
        y = (sh - wh) // 2
    else:
        x = px + (pw - ww) // 2
        y = py + (ph - wh) // 2

    win.geometry(f"+{max(x,0)}+{max(y,0)}")


# ---------- Dialog Tambah/Edit Menu ----------
class MenuDialog(tk.Toplevel):
    def __init__(self, parent, title="Tambah Menu", init_name="", init_price="", init_opsi=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.opsi_entries = []

        form = tk.Frame(self)
        form.pack(padx=10, pady=10, fill="x")

        tk.Label(form, text="Nama Menu:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ent_name = tk.Entry(form, width=30)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)
        self.ent_name.insert(0, init_name)

        tk.Label(form, text="Harga:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ent_price = tk.Entry(form, width=30)
        self.ent_price.grid(row=1, column=1, padx=5, pady=5)
        self.ent_price.insert(0, str(init_price) if init_price != "" else "")

        self.opsi_frame = tk.LabelFrame(self, text="Opsi Tambahan (opsional)")
        self.opsi_frame.pack(padx=10, pady=(0,10), fill="x")

        header = tk.Frame(self.opsi_frame)
        header.pack(fill="x")
        tk.Label(header, text="Nama Opsi", width=20, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(header, text="Harga", width=10, anchor="w").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(header, text="+ Tambah Opsi", command=self.add_opsi_row).grid(row=0, column=2, padx=5)

        self.rows_container = tk.Frame(self.opsi_frame)
        self.rows_container.pack(fill="x")

        if init_opsi:
            for o_name, o_price in init_opsi.items():
                self.add_opsi_row(o_name, o_price)

        btnf = tk.Frame(self)
        btnf.pack(pady=10)
        tk.Button(btnf, text="OK", width=10, command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btnf, text="Batal", width=10, command=self.on_cancel).pack(side="right", padx=5)

        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        center_window(self, parent)
        self.ent_name.focus_set()

    def add_opsi_row(self, nama="", harga=""):
        row = tk.Frame(self.rows_container)
        row.pack(fill="x", padx=5, pady=2)
        ent_opsi = tk.Entry(row, width=25)
        ent_opsi.pack(side="left", padx=5)
        ent_opsi.insert(0, nama)
        ent_harga = tk.Entry(row, width=10)
        ent_harga.pack(side="left", padx=5)
        ent_harga.insert(0, str(harga) if harga != "" else "")
        btn_del = tk.Button(row, text="Hapus", command=lambda r=row: self._del_row(r))
        btn_del.pack(side="left", padx=5)

        self.opsi_entries.append((row, ent_opsi, ent_harga))

    def _del_row(self, row_widget):
        for i, (rw, _, _) in enumerate(self.opsi_entries):
            if rw is row_widget:
                self.opsi_entries.pop(i)
                break
        row_widget.destroy()

    def on_ok(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Nama menu wajib diisi.", parent=self)
            return
        try:
            harga = int(self.ent_price.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Harga harus berupa angka.", parent=self)
            return

        opsi = {}
        for _, ent_opsi, ent_harga in self.opsi_entries:
            o_name = ent_opsi.get().strip()
            if not o_name:
                continue
            try:
                o_price = int(ent_harga.get().strip())
            except ValueError:
                messagebox.showerror("Error", f"Harga opsi '{o_name}' harus angka.", parent=self)
                return
            opsi[o_name] = o_price

        self.result = (name, harga, opsi)
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


# ---------- Dialog Tambah Pesanan ----------
class PesananDialog(tk.Toplevel):
    def __init__(self, parent, nama, harga, opsi_dict):
        super().__init__(parent)
        self.title("Tambah Pesanan")
        self.resizable(False, False)
        self.result = None
        self.opsi_vars = {}

        tk.Label(self, text=f"Menu: {nama} (Rp{harga})").pack(pady=(10,5))

        qty_frame = tk.Frame(self)
        qty_frame.pack(pady=5)
        tk.Label(qty_frame, text="Jumlah:").pack(side="left", padx=(0,5))
        self.qty_var = tk.IntVar(value=1)
        self.spin_qty = tk.Spinbox(qty_frame, from_=1, to=100, textvariable=self.qty_var, width=5)
        self.spin_qty.pack(side="left")

        if opsi_dict:
            tk.Label(self, text="Pilih Opsi Tambahan:").pack()
            box = tk.Frame(self)
            box.pack(pady=5)
            for o, h in opsi_dict.items():
                var = tk.BooleanVar()
                cb = tk.Checkbutton(box, text=f"{o} (+Rp{h}/item)", variable=var)
                cb.pack(anchor="w")
                self.opsi_vars[o] = (var, h)
        else:
            tk.Label(self, text="Menu ini tidak memiliki opsi tambahan.").pack()

        tk.Label(self, text="Catatan (opsional):").pack(pady=(10,0))
        self.ent_catatan = tk.Entry(self, width=40)
        self.ent_catatan.pack(pady=5)

        btnf = tk.Frame(self)
        btnf.pack(pady=10)
        tk.Button(btnf, text="OK", command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btnf, text="Batal", command=self.on_cancel).pack(side="right", padx=5)

        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        center_window(self, parent)

    def on_ok(self):
        selected_opsi = []
        opsi_per_unit = 0
        for o, (var, h) in self.opsi_vars.items():
            if var.get():
                selected_opsi.append(o)
                opsi_per_unit += h

        try:
            qty = max(1, int(self.qty_var.get()))
        except Exception:
            qty = 1
        catatan = self.ent_catatan.get().strip()
        self.result = (selected_opsi, opsi_per_unit, catatan, qty)
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


# ---------- Dialog Checkout opsi tanggal (dengan flag confirmed) ----------
class CheckoutDialog(tk.Toplevel):
    def __init__(self, parent, default_date=None):
        super().__init__(parent)
        self.title("Checkout - Opsi Tanggal")
        self.resizable(False, False)
        self.result = None
        self.confirmed = False  # True jika OK

        frm = tk.Frame(self)
        frm.pack(padx=10, pady=10, fill="x")

        tk.Label(frm, text="Tanggal pemesanan opsional format YYYY-MM-DD:").grid(row=0, column=0, sticky="w")
        self.ent_date = tk.Entry(frm, width=20)
        self.ent_date.grid(row=1, column=0, pady=(4,8), sticky="w")
        if default_date:
            self.ent_date.insert(0, default_date)

        tk.Label(frm, text="Kosongkan untuk transaksi sekarang").grid(row=2, column=0, sticky="w", pady=(0,6))

        btnf = tk.Frame(self)
        btnf.pack(pady=6)
        tk.Button(btnf, text="OK", width=10, command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btnf, text="Batal", width=10, command=self.on_cancel).pack(side="right", padx=5)

        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        center_window(self, parent)

    def on_ok(self):
        s = self.ent_date.get().strip()
        if not s:
            # kosongkan berarti sekarang
            self.result = None
            self.confirmed = True
            self.destroy()
            return
        try:
            datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Format salah", "Tanggal harus dalam format YYYY-MM-DD.", parent=self)
            return
        self.result = s
        self.confirmed = True
        self.destroy()

    def on_cancel(self):
        self.confirmed = False
        self.result = None
        self.destroy()


# ---------- Aplikasi Utama ----------
class KasirApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kasir Sederhana")
        self.menu_data = load_menu()
        self.keranjang = []

        left = tk.LabelFrame(root, text="Daftar Menu")
        left.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self.tree_menu = ttk.Treeview(left, columns=("Harga", "Opsi"), show="headings")
        self.tree_menu.heading("Harga", text="Harga")
        self.tree_menu.heading("Opsi", text="Opsi Tambahan")
        self.tree_menu.column("Harga", width=100, anchor="center")
        self.tree_menu.column("Opsi", width=300, anchor="w")
        self.tree_menu.pack(fill="both", expand=True)

        menu_btns = tk.Frame(left)
        menu_btns.pack(pady=6)
        tk.Button(menu_btns, text="Tambah Menu", command=self.add_menu).pack(side="left", padx=3)
        tk.Button(menu_btns, text="Edit Menu", command=self.edit_menu).pack(side="left", padx=3)
        tk.Button(menu_btns, text="Hapus Menu", command=self.delete_menu).pack(side="left", padx=3)
        tk.Button(menu_btns, text="Pesan", command=self.add_pesanan).pack(side="left", padx=3)

        right = tk.LabelFrame(root, text="Keranjang")
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        self.tree_cart = ttk.Treeview(right, columns=("Menu", "Qty", "Opsi", "Subtotal", "Catatan"), show="headings")
        self.tree_cart.heading("Menu", text="Menu")
        self.tree_cart.heading("Qty", text="Qty")
        self.tree_cart.heading("Opsi", text="Opsi")
        self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.heading("Catatan", text="Catatan")
        self.tree_cart.column("Menu", width=180, anchor="w")
        self.tree_cart.column("Qty", width=50, anchor="center")
        self.tree_cart.column("Opsi", width=200, anchor="w")
        self.tree_cart.column("Subtotal", width=100, anchor="center")
        self.tree_cart.column("Catatan", width=200, anchor="w")
        self.tree_cart.pack(fill="both", expand=True)

        cart_btns = tk.Frame(right)
        cart_btns.pack(pady=6)
        tk.Button(cart_btns, text="Hapus Item", command=self.remove_item).pack(side="left", padx=3)
        tk.Button(cart_btns, text="Checkout", command=self.checkout).pack(side="left", padx=3)

        self.total_lbl = tk.Label(right, text="Total: Rp0", font=("Arial", 11, "bold"))
        self.total_lbl.pack(anchor="e", padx=10, pady=(0,6))

        self.refresh_menu()
        self.refresh_cart()

    def _selected_menu_name(self):
        sel = self.tree_menu.focus()
        if not sel:
            return None
        return sel

    def refresh_menu(self):
        for i in self.tree_menu.get_children():
            self.tree_menu.delete(i)
        for name, data in self.menu_data.items():
            opsi_str = ", ".join([f"{o} (+Rp{h})" for o, h in data.get("opsi", {}).items()]) if data.get("opsi") else "-"
            self.tree_menu.insert("", "end", iid=name, values=(f"Rp{data['harga']}", opsi_str))

    def refresh_cart(self):
        for i in self.tree_cart.get_children():
            self.tree_cart.delete(i)
        total = 0
        for idx, item in enumerate(self.keranjang):
            opsi_str = ", ".join(item["opsi"]) if item["opsi"] else "-"
            self.tree_cart.insert("", "end", iid=str(idx),
                                  values=(item["nama"], item["qty"], opsi_str, f"Rp{item['subtotal']}", item["catatan"]))
            total += item["subtotal"]
        self.total_lbl.config(text=f"Total: Rp{total}")

    def add_menu(self):
        dlg = MenuDialog(self.root, title="Tambah Menu")
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        name, harga, opsi = dlg.result

        if name in self.menu_data:
            messagebox.showerror("Duplikat", "Nama menu sudah ada. Gunakan nama lain.", parent=self.root)
            return

        self.menu_data[name] = {"harga": harga, "opsi": opsi}
        save_menu(self.menu_data)
        log_action("TAMBAH_MENU", name)
        self.refresh_menu()

    def edit_menu(self):
        name = self._selected_menu_name()
        if not name:
            messagebox.showinfo("Info", "Pilih menu yang akan diedit.", parent=self.root)
            return
        data = self.menu_data.get(name)
        if not data:
            messagebox.showerror("Error", "Data menu tidak ditemukan.", parent=self.root)
            return

        old_name = name
        old_price = data["harga"]
        old_opsi = data.get("opsi", {})

        dlg = MenuDialog(self.root, title="Edit Menu", init_name=old_name, init_price=old_price, init_opsi=old_opsi)
        self.root.wait_window(dlg)
        if not dlg.result:
            return

        new_name, new_price, new_opsi = dlg.result

        if new_name != old_name and new_name in self.menu_data:
            messagebox.showerror("Duplikat", "Nama menu baru sudah ada.", parent=self.root)
            return

        if new_name != old_name:
            self.menu_data.pop(old_name)
        self.menu_data[new_name] = {"harga": new_price, "opsi": new_opsi}

        save_menu(self.menu_data)
        log_action("EDIT_MENU", f"{old_name} -> {new_name}, Rp{old_price} -> Rp{new_price}")
        self.refresh_menu()

    def delete_menu(self):
        name = self._selected_menu_name()
        if not name:
            messagebox.showinfo("Info", "Pilih menu yang akan dihapus.", parent=self.root)
            return
        if messagebox.askyesno("Konfirmasi", f"Hapus menu '{name}'?", parent=self.root):
            self.menu_data.pop(name, None)
            save_menu(self.menu_data)
            log_action("HAPUS_MENU", name)
            self.refresh_menu()

    def add_pesanan(self):
        name = self._selected_menu_name()
        if not name:
            messagebox.showinfo("Info", "Pilih menu yang ingin dipesan.", parent=self.root)
            return
        data = self.menu_data.get(name)
        if not data:
            messagebox.showerror("Error", "Data menu tidak ditemukan.", parent=self.root)
            return

        harga = data["harga"]
        opsi_dict = data.get("opsi", {})

        dlg = PesananDialog(self.root, nama=name, harga=harga, opsi_dict=opsi_dict)
        self.root.wait_window(dlg)
        if not dlg.result:
            return

        selected_opsi, opsi_per_unit, catatan, qty = dlg.result
        subtotal = qty * (harga + opsi_per_unit)

        item = {
            "nama": name,
            "harga": harga,
            "opsi": selected_opsi,
            "catatan": catatan,
            "qty": qty,
            "subtotal": subtotal
        }
        self.keranjang.append(item)
        log_action("TAMBAH_PESANAN", f"{name} x{qty} subtotal Rp{subtotal}")
        self.refresh_cart()

    def remove_item(self):
        sel = self.tree_cart.focus()
        if not sel:
            messagebox.showinfo("Info", "Pilih item yang akan dihapus dari keranjang.", parent=self.root)
            return
        idx = int(sel)
        if 0 <= idx < len(self.keranjang):
            removed = self.keranjang.pop(idx)
            log_action("HAPUS_ITEM", f"{removed['nama']} x{removed['qty']} subtotal Rp{removed['subtotal']}")
            self.refresh_cart()

    def checkout(self):
        if not self.keranjang:
            messagebox.showinfo("Info", "Keranjang kosong.", parent=self.root)
            return
        total = sum(item["subtotal"] for item in self.keranjang)

        dlg = CheckoutDialog(self.root, default_date=datetime.now().strftime("%Y-%m-%d"))
        self.root.wait_window(dlg)

        # Jika user menekan Batal -> dlg.confirmed == False -> batalkan checkout
        if not getattr(dlg, "confirmed", False):
            return

        scheduled_date = dlg.result  # None atau 'YYYY-MM-DD'

        with open(PESANAN_FILE, "a", encoding="utf-8") as f:
            f.write("=== PESANAN BARU ===\n")
            f.write(f"Dicatat: {now_str()}\n")
            if scheduled_date:
                f.write(f"Jadwal Pesanan: {scheduled_date}\n")
            else:
                f.write("Jadwal Pesanan: Sekarang\n")
            for item in self.keranjang:
                opsi_str = ", ".join(item["opsi"]) if item["opsi"] else "-"
                catatan_str = item["catatan"] if item["catatan"] else "-"
                f.write(f"- {item['nama']} x{item['qty']} (Rp{item['harga']}/item)\n")
                f.write(f"  Opsi: {opsi_str}\n")
                f.write(f"  Catatan: {catatan_str}\n")
                f.write(f"  Subtotal: Rp{item['subtotal']}\n")
            f.write(f"TOTAL: Rp{total}\n")
            f.write("====================\n\n")

        log_action("CHECKOUT", f"{len(self.keranjang)} item, total Rp{total}, jadwal: {scheduled_date or 'now'}")
        self.keranjang.clear()
        self.refresh_cart()
        messagebox.showinfo("Sukses", f"Checkout berhasil.\nTotal: Rp{total}", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = KasirApp(root)
    root.mainloop()
