import random
def roll_dice():
    return random.randint(1, 6)

print("Selamat datang di simulasi dadu! Tekan Enter untuk melempar dadu atau ketik 'exit' untuk keluar.")
while True:
    user_input = input("Lempar dadu? (Tekan Enter/ketik 'exit'): ").strip().lower()

    if user_input == "exit":
        print("Terima kasih telah bermain!")
        break
    hasil = roll_dice()
    print(f"🎲 Kamu mendapatkan angka: {hasil}")