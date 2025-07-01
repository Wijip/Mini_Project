import tkinter as tk
import random

target = random.randint(1, 100)
max_attempt = 10
def check(attempt):
    try:
        guess = int(entry.get())
        attempt += 1
        if guess < target:
            hasil_label.config(text=f"Terlalu rendah! ({max_attempt - attempt} kesempatan lagi)")
        elif guess > target:
            hasil_label.config(text=f"Terlalu tinggi! ({max_attempt - attempt} kesempatan lagi)")
        else:
            hasil_label.config(text=f"Selamat! Angka yang benar adalah {target}.", fg="black")
            entry.config(state="disabled")
            tebak_button.config(state="disabled")
    except ValueError:
        hasil_label.config(text="Harap Masukkan angka yang valid!", fg="black")
    return attempt
root = tk.Tk()
root.title("Permainan tebak angka")
root.geometry("400x300")

intruction_label = tk.Label(root, text=f"tebak angka antara 1 hingga 100\nKamu memiliki {max_attempt} kesempatan", font=("Arial", 12), justify="center")
intruction_label.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 12))
entry.pack(pady=5)
attempt =0

tebak_button = tk.Button(root, text="Cek tebakan",command=lambda : check(attempt), font=("Arial",12))
tebak_button.pack(pady=5)
hasil_label = tk.Label(root, text="", font=("Arial", 12))
hasil_label.pack(pady=10)

root.mainloop()