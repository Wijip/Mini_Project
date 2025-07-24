import tkinter as tk
from tkinter import messagebox

class OrderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Warung Makan GUI")
        self.geometry("500x380")
        self.resizable(False, False)

        # Daftar menu dan harga
        self.menu = {
            "Nasi Goreng": 20000,
            "Mie Goreng": 18000,
            "Nasi Rawon": 20000,
            "Nasi Pecel": 15000,
            "Es Jeruk": 5000,
            "Jus Apel": 10000,
            "Jus Alpukat": 12000,
            "Jus Mangga": 10000,
            "Pisang Goreng": 7000
        }
        self.cart = {}  # key: nama menu, value: qty

        self._build_widgets()
        self._update_price()   # inisialisasi price label
        self._update_cart()

    def _build_widgets(self):
        left = tk.Frame(self, padx=10, pady=10)
        left.pack(side="left", fill="y")

        tk.Label(left, text="Pilih Menu:", font=("Arial", 12)).pack(anchor="w")

        # List opsi dengan placeholder di depan
        self.options = ["Pilih Menu"] + list(self.menu.keys())
        self.selected_food = tk.StringVar(value=self.options[0])
        om = tk.OptionMenu(left, self.selected_food, *self.options)
        om.pack(fill="x")

        # Label harga
        self.price_var = tk.StringVar()
        tk.Label(left, textvariable=self.price_var,
                 font=("Arial", 12), fg="blue").pack(anchor="w", pady=(5,10))

        # trace pilihan untuk update harga & tombol
        self.selected_food.trace_add('write', self._update_price)

        tk.Label(left, text="Jumlah:", font=("Arial", 12)).pack(anchor="w")
        self.qty_spin = tk.Spinbox(left, from_=1, to=20, width=5, state="disabled")
        self.qty_spin.pack(fill="x", pady=(0, 10))

        # tombol tambah ke cart
        self.add_btn = tk.Button(left, text="Tambah ke Keranjang",
                                 command=self.add_to_cart, state="disabled")
        self.add_btn.pack(pady=(5, 0), fill="x")

        # kanan: keranjang
        right = tk.Frame(self, padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="Keranjang Anda:", font=("Arial", 12)).pack(anchor="w")
        self.cart_listbox = tk.Listbox(right, height=12)
        self.cart_listbox.pack(fill="both", expand=True)

        self.total_var = tk.StringVar(value="Total: Rp 0")
        tk.Label(right, textvariable=self.total_var,
                 font=("Arial", 14, "bold")).pack(pady=(10, 0), anchor="e")

        btn_frame = tk.Frame(right)
        btn_frame.pack(pady=10, anchor="e")
        tk.Button(btn_frame, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Place Order", command=self.place_order).pack(side="left")

    def _update_price(self, *args):
        """Update harga & aktifkan tombol hanya jika menu valid."""
        choice = self.selected_food.get()
        if choice == "Pilih Menu":
            self.price_var.set("Harga: -")
            self.add_btn.config(state="disabled")
            self.qty_spin.config(state="disabled")
        else:
            harga = self.menu[choice]
            self.price_var.set(f"Harga: Rp {harga:,}")
            self.add_btn.config(state="normal")
            self.qty_spin.config(state="normal")

    def add_to_cart(self):
        food = self.selected_food.get()
        if food == "Pilih Menu":
            messagebox.showerror("Error", "Silakan pilih menu terlebih dahulu.")
            return

        try:
            qty = int(self.qty_spin.get())
            if qty < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan jumlah valid (>=1).")
            return

        self.cart[food] = self.cart.get(food, 0) + qty
        self._update_cart()

    def _update_cart(self):
        self.cart_listbox.delete(0, tk.END)
        total = 0
        for food, qty in self.cart.items():
            subtotal = self.menu[food] * qty
            total += subtotal
            self.cart_listbox.insert(
                tk.END, f"{food} x {qty}  —  Rp {subtotal:,}"
            )
        self.total_var.set(f"Total: Rp {total:,}")

    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Confirm", "Bersihkan semua pesanan?"):
            self.cart.clear()
            self._update_cart()

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Keranjang Kosong", "Belum ada item di keranjang.")
            return

        with open("pesanan.txt", "a", encoding="utf-8") as f:
            f.write("Pesanan Baru:\n")
            for food, qty in self.cart.items():
                f.write(f"{food} | Qty: {qty} | Subtotal: Rp {self.menu[food]*qty:,}\n")
            f.write("-------------------------------\n")

        messagebox.showinfo("Sukses", "Pesanan berhasil disimpan!")
        self.cart.clear()
        self._update_cart()

        # Reset pilihan ke placeholder
        self.selected_food.set("Pilih Menu")



if __name__ == '__main__':
    app = OrderApp()
    app.mainloop()