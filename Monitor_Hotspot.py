import re
import time
import schedule
import getpass
from netmiko import ConnectHandler

def parse_kv_line(line):
    """
    Parse string bertipe 'key=val key2=val2...' menjadi dict.
    Mendukung nilai tanpa spasi atau dalam tanda kutip.
    """
    pattern = re.compile(r'([^=\s]+)=(".*?"|\S+)')
    data = {}
    for match in pattern.finditer(line):
        key, val = match.groups()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        data[key] = val
    return data

def fetch_user_quotas(connection):
    """
    Ambil limit-bytes-total untuk setiap user hotspot.
    Mengembalikan dict: { username: quota_bytes, ... }
    """
    output = connection.send_command(
        '/ip hotspot user print detail without-paging'
    )
    quotas = {}
    for line in output.splitlines():
        if re.match(r'^\s*\d+', line):
            kv = parse_kv_line(line)
            name  = kv.get('name')
            limit = int(kv.get('limit-bytes-total', 0))
            if name:
                quotas[name] = limit
    return quotas

def monitor_traffic():
    """
    Ambil data sesi aktif, hitung total dan tampilkan bersama kuota.
    Dipanggil tiap 1 menit oleh schedule.
    """
    output = conn.send_command(
        '/ip hotspot active print detail without-paging'
    )
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    header = f"[{timestamp}] Hotspot Traffic & Quota Usage"
    print('\n' + header)
    print('-' * len(header))
    print(f"{'User':15} {'Download':12} {'Upload':12} {'Total':12} {'Quota':12}")
    print('-' * 65)

    for line in output.splitlines():
        if re.match(r'^\s*\d+', line):
            kv   = parse_kv_line(line)
            user = kv.get('user', '<unknown>')
            jin  = int(kv.get('bytes-in', 0))
            jout = int(kv.get('bytes-out', 0))
            total = jin + jout
            quota = user_quotas.get(user, 0)
            print(f"{user:15} {jin:12d} {jout:12d} {total:12d} {quota:12d}")

if __name__ == '__main__':
    # 1. Input kredensial RouterOS
    router_ip = input("Router IP       : ").strip()
    username  = input("Username        : ").strip()
    password  = getpass.getpass("Password        : ")

    # 2. Koneksi ke MikroTik via Netmiko
    conn = ConnectHandler(
        device_type='mikrotik_routeros',
        host=router_ip,
        username=username,
        password=password
    )
    print("\nKoneksi berhasil. Mengambil data kuota user...\n")

    # 3. Fetch kuota user sekali di awal
    user_quotas = fetch_user_quotas(conn)

    # 4. Jadwalkan monitoring tiap 1 menit
    schedule.every(1).minutes.do(monitor_traffic)
    print("Monitoring dimulai (update tiap 1 menit). Tekan Ctrl+C untuk berhenti.\n")

    try:
        # Jalankan loop schedule
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring dihentikan, memutus koneksi...")
        conn.disconnect()
        print("Selesai.")
