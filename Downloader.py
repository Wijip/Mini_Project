import requests

def download_file(url, filename=None):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        if filename is None:
            filename = url.split("/")[-1]

        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"✅ File Berhasil diunduh: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Terjadi Kesalahan: {e}")

file_url = input("Masukkan URL file yang ingin diunduh: ")
download_file(file_url)