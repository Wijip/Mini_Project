from pytube import YouTube

def download_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        print(f"Mengunduh: {yt.title}")
        stream.download()
        print(f"✅ Unudhan Selesai")

    except Exception as e:
        print(f"❌ Terjadi Kesalahan: {e}")
video_url = input("Masukkan URL video YouTube: ")
download_video(video_url)