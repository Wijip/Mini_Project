import tkinter as tk
import random

def roll_dice():
    result = random.randint(1, 6)
    dice_label.config(text=f"🎲 {result}")

root = tk.Tk()
root.title("Simulasi Dadu")
root.geometry("300x200")

dice_label = tk.Label(root, text="🎲 Tekan tombol untuk melempar", font=("Arial", 14))
dice_label.pack(pady=20)
roll_button = tk.Button(root, text="Lempar Dadu", command=roll_dice, font=("Arial", 12))
roll_button.pack(pady=10)

root.mainloop()