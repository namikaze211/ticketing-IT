# Sistem Ticketing & Helpdesk IT (Monitoring Masalah per Departemen)

Aplikasi Web Helpdesk IT modern yang dirancang untuk **mencatat, memantau, dan menganalisis kendala/trobel teknis IT di setiap departemen**.

---

## 🚀 Fitur Utama

1. **Analisis Trobel per Departemen (Mengetahui Gangguan di Departemen Mana Saja)**:
   - **Visual Bar Chart**: Peringkat departemen dengan kendala terbanyak.
   - **Visual Donut Chart**: Kategori kendala dominan (Hardware, Jaringan, Printer, Software, ERP, dll.).
   - **Tabel Peringkat Trobel**: Menampilkan total kasus, status (Menunggu, Diproses, Selesai), dan rasio penyelesaian tiap departemen.
   - **Halaman Analitik Khusus**: Rincian kendala apa saja yang sering terjadi di departemen tertentu (contoh: Gudang -> Printer Barcode & Hardware; Finance -> e-Faktur & Printer; Produksi -> Jaringan Wi-Fi).

2. **Portal Pengguna (Untuk Seluruh Karyawan / Departemen)**:
   - Formulir pembuatan tiket yang mudah digunakan.
   - Input nama pelapor, pilih departemen, lokasi ruangan, nomor telepon/ext, kategori masalah, prioritas, judul, dan deskripsi detail.
   - Nomor tiket otomatis (Format: `TIK-YYYYMMDD-XXX`).
   - Fitur **Lacak Tiket** secara mandiri menggunakan nomor tiket.

3. **Panel Manajemen Tiket untuk Tim IT**:
   - Filter cepat berdasarkan: **Departemen**, **Status**, **Kategori**, dan **Pencarian Bebas**.
   - Detail tiket: Update status pengerjaan (*Menunggu*, *Sedang Dikerjakan*, *Selesai*).
   - Penugasan nama teknisi IT (*Technician Assignment*).
   - Catatan solusi/tindakan perbaikan (*Knowledge Base Solusi*).
   - Hapus tiket atau cetak bukti pengerjaan.

4. **Ekspor Laporan ke Excel (`.xlsx`)**:
   - Satu klik untuk mengunduh rekapitulasi lengkap dalam format Excel yang siap diserahkan ke Manajemen.
   - Terdiri dari 2 lembar kerja (Sheet):
     - **Sheet 1: Rekap Per Departemen** (Total kasus, status menunggu, diproses, selesai).
     - **Sheet 2: Daftar Seluruh Tiket** (Detail lengkap pelapor, kendala, teknisi, solusi, dan tanggal).

5. **Pengaturan Master Data**:
   - Tambah/hapus Departemen sesuai struktur perusahaan.
   - Tambah/hapus Kategori Masalah IT.

---

## 🛠️ Cara Menjalankan

### Cara 1: Menggunakan File Batch (Paling Praktis)
Cukup **double-click** file:
`run.bat`

### Cara 2: Melalui Terminal / Command Prompt
```bash
python app.py
```

---

## 🖥️ Panduan Deploy ke Server (Production)

Sistem ini sangat fleksibel dan siap dipasang di server kantor:

### Opsi 1: Pasang di Windows Server / PC Kantor
1. Salin seluruh folder `sistem ticketing IT` ke komputer Server.
2. Pastikan Python 3.10+ sudah terinstal di server.
3. Klik ganda file **[`run_server.bat`](file:///c:/Users/itdept3/Music/sistem%20ticketing%20IT/run_server.bat)** (menggunakan **Waitress WSGI Server** yang cepat, multi-threaded, dan stabil untuk melayani banyak pengguna secara bersamaan).
4. **Agar jalan otomatis saat Windows menyala (Auto-start / Background Service):**
   - Tekan `Win + R`, ketik `shell:startup`, lalu buat shortcut file `run_server.bat` di folder tersebut.
   - Atau gunakan **Windows Task Scheduler** dengan trigger *"At startup"*.

### Opsi 2: Pasang di Linux Server (Ubuntu / Debian / CentOS)
1. Salin folder aplikasi ke server Linux (misal di `/var/www/ticketing`).
2. Buat virtual environment & install dependensi:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Jalankan server dengan Waitress atau Gunicorn:
   ```bash
   python3 server.py
   # atau menggunakan Gunicorn:
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
4. (Opsional) Pasang Nginx sebagai Reverse Proxy dan jadikan systemd service (`systemctl enable ticketing`).

### Opsi 3: Pasang Menggunakan Docker (Paling Praktis & Portable)
Jika server Anda sudah memiliki Docker:
```bash
docker compose up -d --build
```
Aplikasi akan langsung berjalan di background pada port `5000` dengan database tersimpan aman di host.

---

## 🌐 Alamat Akses (URL)

| Pengguna | Alamat URL | Keterangan |
| :--- | :--- | :--- |
| **Karyawan / Departemen Lain** | `http://161.60.11.15:5000` atau `http://localhost:5000` | Formulir Buat Tiket & Cek Status |
| **Tim IT (Dashboard Analisis)** | `http://localhost:5000/it/dashboard` | Dashboard Statistik Trobel per Departemen |
| **Tim IT (Daftar Tiket)** | `http://localhost:5000/it/tiket` | Kelola dan proses tiket masuk |
| **Tim IT (Analisis Dept)** | `http://localhost:5000/it/departemen` | Matriks masalah khusus per departemen |

> **Catatan Jaringan**: Selama komputer IT terhubung ke jaringan LAN / Wi-Fi kantor, rekan kerja dari departemen lain dapat membuka `http://161.60.11.15:5000` langsung dari browser laptop atau HP mereka.
