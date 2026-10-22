import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "ticketing.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabel Departemen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    """)

    # Tabel Kategori Masalah
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    """)

    # Tabel Tiket
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_number TEXT UNIQUE NOT NULL,
        reporter_name TEXT NOT NULL,
        department TEXT NOT NULL,
        location TEXT,
        contact TEXT,
        category TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'Normal',
        subject TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Menunggu',
        technician TEXT DEFAULT '',
        solution TEXT DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME
    )
    """)

    # Default Departments jika belum ada
    default_depts = [
        ("Finance & Accounting", "Keuangan dan Pembukuan"),
        ("Human Resources (HRD)", "Sumber Daya Manusia & Personalia"),
        ("Produksi / Operasional", "Lantai Produksi dan Mesin"),
        ("Gudang & Logistik", "Warehouse dan Distribusi"),
        ("Marketing & Sales", "Pemasaran dan Penjualan"),
        ("Purchasing / Pengadaan", "Pengadaan Barang dan Supplier"),
        ("Quality Control (QC)", "Pengawasan Kualitas"),
        ("General Affairs (GA)", "Umum dan Fasilitas"),
        ("Direksi / Manajemen", "Pimpinan Eksekutif")
    ]
    for name, desc in default_depts:
        cursor.execute("INSERT OR IGNORE INTO departments (name, description) VALUES (?, ?)", (name, desc))

    # Default Categories jika belum ada
    default_cats = [
        ("Jaringan & Internet", "Wi-Fi lemot, kabel LAN putus, tidak bisa akses server"),
        ("Hardware / Komputer", "PC mati, monitor rusak, keyboard/mouse rusak, lambat"),
        ("Printer & Scanner", "Paper jam, tinta habis, printer offline, tidak terdeteksi"),
        ("Software & Aplikasi", "Aplikasi crash, error lisensi, install aplikasi kerja"),
        ("Email & Komunikasi", "Outlook error, kapasitas mailbox penuh, reset password"),
        ("Sistem ERP / Database", "Akses menu terkunci, data tidak sinkron, error input"),
        ("Keamanan & Antivirus", "Terkena virus/malware, flashdisk terblokir, pop-up aneh"),
        ("Lain-lain", "Kebutuhan IT lainnya")
    ]
    for name, desc in default_cats:
        cursor.execute("INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)", (name, desc))

    # Cek apakah sudah ada tiket, jika belum ada buatkan sample data agar statistik langsung terlihat menarik
    cursor.execute("SELECT COUNT(*) FROM tickets")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_tickets = [
            ("TIK-20261019-001", "Budi Santoso", "Finance & Accounting", "Lt. 2 R. Finance", "08123456789", "Printer & Scanner", "Tinggi", "Printer dot-matrix faktur macet / paper jam", "Printer Epson LX-310 tidak bisa menarik kertas faktur pajak, mohon bantuannya karena mau closing bulanan.", "Sedang Dikerjakan", "Ahmad (IT Support)", "", "2026-10-19 08:30:00", "2026-10-19 09:15:00", None),
            ("TIK-20261019-002", "Siti Rahma", "Human Resources (HRD)", "Lt. 1 R. HRD", "Ext 104", "Software & Aplikasi", "Normal", "Software Fingerprint/Absensi tidak mau sync", "Data absensi pagi ini belum masuk ke server payroll, ada notifikasi timeout connection.", "Menunggu", "", "", "2026-10-19 08:45:00", "2026-10-19 08:45:00", None),
            ("TIK-20261019-003", "Hendra Wijaya", "Gudang & Logistik", "Gudang B Pos 2", "08567891234", "Hardware / Komputer", "Darurat", "Komputer barcode scanner mati total (blue screen)", "PC di gate loading barang mati mendadak saat scan barang masuk, display layar biru. Truk antri.", "Selesai", "Rian (IT Infra)", "RAM dibersihkan dan dicek slotnya, sistem Windows sudah normal kembali.", "2026-10-19 07:15:00", "2026-10-19 08:05:00", "2026-10-19 08:05:00"),
            ("TIK-20261019-004", "Dewi Lestari", "Marketing & Sales", "Lt. 3 R. Sales", "Ext 305", "Email & Komunikasi", "Rendah", "Kapasitas mailbox Outlook hampir penuh (95%)", "Muncul peringatan storage mailbox 95%. Butuh bantuan untuk arsip (archive) email tahun lalu.", "Menunggu", "", "", "2026-10-19 09:10:00", "2026-10-19 09:10:00", None),
            ("TIK-20261019-005", "Agus Setiawan", "Produksi / Operasional", "Workshop 1", "08198765432", "Jaringan & Internet", "Tinggi", "Koneksi Wi-Fi area produksi terputus", "Access point produksi lampu indikator merah, operator tidak bisa buka work order.", "Sedang Dikerjakan", "Rian (IT Infra)", "Kabel POE switch diperiksa, sedang crimping ulang konektor RJ45.", "2026-10-19 09:30:00", "2026-10-19 10:00:00", None),
            ("TIK-20261019-006", "Rina Marlina", "Purchasing / Pengadaan", "Lt. 2 R. Purchase", "Ext 202", "Sistem ERP / Database", "Normal", "Tidak bisa approve PO di sistem ERP", "Muncul error 'Session expired or role unauthorized' saat tombol approve ditekan.", "Selesai", "Ahmad (IT Support)", "Hak akses user telah diperbarui di database master ERP.", "2026-10-18 14:20:00", "2026-10-18 15:10:00", "2026-10-18 15:10:00"),
            ("TIK-20261019-007", "Fajar Nugraha", "Produksi / Operasional", "Ruang Kontrol QA", "Ext 401", "Hardware / Komputer", "Normal", "PC timbangan digital lambat sekali / sering hang", "Aplikasi timbangan berat sering not responding setelah update Windows.", "Menunggu", "", "", "2026-10-19 10:15:00", "2026-10-19 10:15:00", None),
            ("TIK-20261019-008", "Sri Wahyuni", "Finance & Accounting", "Lt. 2 R. Pajak", "08134567890", "Software & Aplikasi", "Tinggi", "e-Faktur DJP tidak bisa upload faktur", "Muncul kode error ETAX-40001 tidak dapat menghubungi service DJP.", "Selesai", "Ahmad (IT Support)", "Sertifikat elektronik diperbarui dan setting proxy disesuaikan.", "2026-10-17 11:00:00", "2026-10-17 11:45:00", "2026-10-17 11:45:00"),
            ("TIK-20261019-009", "Bambang Tri", "Gudang & Logistik", "Gudang A Racking", "08129876543", "Printer & Scanner", "Normal", "Printer label barcode zebra hasil cetak buram", "Head printer sepertinya kotor atau ribbon kendur, barcode tidak terbaca scanner.", "Sedang Dikerjakan", "Ahmad (IT Support)", "Head thermal printer sedang dibersihkan dengan alkohol 90%.", "2026-10-19 10:30:00", "2026-10-19 10:45:00", None)
        ]
        cursor.executemany("""
        INSERT INTO tickets (ticket_number, reporter_name, department, location, contact, category, priority, subject, description, status, technician, solution, created_at, updated_at, resolved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_tickets)

    conn.commit()
    conn.close()

def generate_ticket_number():
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"TIK-{today_str}-"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticket_number FROM tickets WHERE ticket_number LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
    last = cursor.fetchone()
    conn.close()

    if last:
        last_num = int(last["ticket_number"].split("-")[-1])
        new_num = f"{last_num + 1:03d}"
    else:
        new_num = "001"
    return f"{prefix}{new_num}"

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
