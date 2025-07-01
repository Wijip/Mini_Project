import speedtest

def bandwidth_test():
    print("Mengukur kecepatan internet...")

    st = speedtest.Speedtest()
    st.get_best_server()

    download_speed = st.download() / 1_000_000  # Konversi ke Mbps
    upload_speed = st.upload() / 1_000_000  # Konversi ke Mbps
    ping = st.results.ping

    print(f"Kecepatan Unduh: {download_speed:.2f} Mbps")
    print(f"Kecepatan Unggah: {upload_speed:.2f} Mbps")
    print(f"Ping: {ping} ms")

# Menjalankan tes kecepatan
bandwidth_test()
