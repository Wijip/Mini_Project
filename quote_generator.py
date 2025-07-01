import random

quotes = [
    "Jangan menunggu waktu yang tepat, Buatlah waktu itu tepat.",
    "Keberhasilan adalah hasil dari kerja keras dan ketekunan.",
    "Hidup adalah petualangan yang penuh dengan peluang.",
    "Kesuksesan dumulai dari mimpi, kemudian menjadi rencana dan akhirnya tindakan",
    "Setiap hari adalah kesempatan baru untuk belajar dan tumbuh."
]

def generate_quote():
    return random.choice(quotes)

if __name__ == "__main__":
    print(f"Quote hari ini : {generate_quote()}")