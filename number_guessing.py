import random
target = random.randint(1, 100)
percobaan = 0
max_attempt = 10

print("Selamat datang di permainan tebak angka: ")
print("Coba tebak angka antara 1 hingga 100.")

while True:
    try:
        guess = int(input("Masukkan tebakanmu: "))
        percobaan += 1

        if guess < target:
            print(f"Terlalu rendah!! Coba angka lebih besar. {max_attempt - percobaan} Kesempatan tersisa")
        elif guess > target:
            print(f"Terlalu tinggi!! Coba angka lebih kecil. {max_attempt - percobaan} Kesempatan tersisa")
        else:
            print(f"Selamat! Kamu berhasil menebak angka {target} dalam {percobaan} percobaan")
            break
    except ValueError:
        print("Harap masukkan angka yang valid")
    if percobaan == max_attempt:
        print("Yahh, Percobaan telah habis. Coba lagi lain waktu.")
        break