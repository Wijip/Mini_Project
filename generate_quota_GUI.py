import tkinter as tk
import random

quotes = [
    "Jangan menunggu waktu yang tepat, Buatlah waktu itu tepat.",
    "Keberhasilan adalah hasil dari kerja keras dan ketekunan.",
    "Hidup adalah petualangan yang penuh dengan peluang.",
    "Kesuksesan dumulai dari mimpi, kemudian menjadi rencana dan akhirnya tindakan",
    "Setiap hari adalah kesempatan baru untuk belajar dan tumbuh."
]

def generate_quote():
    quote_label.config(text=random.choice(quotes))

root = tk.Tk()
root.title("Quote Generator")
root.geometry("400x300")

quote_label = tk.Label(root, text="Klik tombol untuk mendapatkan kutipan!", wraplength=350, font=("Arial", 12), justify="center")
quote_label.pack(pady=20)

generate_button = tk.Button(root, text="Dapatkan kutipan", command=generate_quote, font=("Arial", 12))
generate_button.pack(pady=20)
root.mainloop()