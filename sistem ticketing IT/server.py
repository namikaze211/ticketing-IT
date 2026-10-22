"""
Production Server Runner untuk Sistem Ticketing IT
Menggunakan Waitress (Production-grade WSGI Server)
Mendukung multi-threading, koneksi bersamaan, dan stabil untuk server kantor.
"""
import os
import sys
from app import app
from database import init_db

# Port default: 5000 (bisa diubah via environment variable PORT, misal port 80 untuk HTTP standar)
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
THREADS = int(os.environ.get("THREADS", 8))

if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("   SISTEM TICKETING IT - PRODUCTION SERVER (WAITRESS)")
    print("=" * 60)
    print(f" * Server Berjalan di : http://{HOST}:{PORT}")
    print(f" * Akses Lokal Komputer: http://localhost:{PORT}")
    print(f" * Worker Threads     : {THREADS}")
    print(f" * Status Mode        : PRODUCTION (Multi-threaded & Stable)")
    print("=" * 60)
    print(" Tekan CTRL + C untuk menghentikan server.")
    print("=" * 60)

    try:
        from waitress import serve
        serve(app, host=HOST, port=PORT, threads=THREADS)
    except ImportError:
        print("[PERINGATAN] Waitress belum terpasang, beralih ke server bawaan Flask...")
        app.run(host=HOST, port=PORT, debug=False)
