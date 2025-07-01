import tkinter as tk
from pytube import YouTube

def download_video():
    url = url_entry.get()
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        status_label.config(text=f"Mengunduh: {yt.title}...", fg="blue")
        stream.download()
        status_label.config(text="✅ Unduhan selesai!", fg="green")
    except Exception as e:
        status_label.config(text=f"❌ Error: {e}", fg="red")

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("400x200")

url_label = tk.Label(root, text="Masukkan URL YouTube:", font=("Arial", 12))
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=40, font=("Arial", 12))
url_entry.pack(pady=5)

download_button = tk.Button(root, text="Unduh Video", command=download_video, font=("Arial", 12))
download_button.pack(pady=10)
status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=10)

root.mainloop()