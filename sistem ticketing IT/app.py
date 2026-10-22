import os
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import pandas as pd
from database import get_db_connection, init_db, generate_ticket_number

app = Flask(__name__)
app.secret_key = "it_ticketing_secret_key_dept3"

# Inisialisasi DB saat aplikasi pertama kali dijalankan
init_db()

@app.route("/")
def index():
    """Halaman Utama / Portal Pengguna untuk Buat Tiket"""
    conn = get_db_connection()
    departments = conn.execute("SELECT * FROM departments ORDER BY name ASC").fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
    
    # Ambil 5 tiket terbaru untuk quick preview
    recent_tickets = conn.execute("""
        SELECT ticket_number, reporter_name, department, category, priority, status, created_at 
        FROM tickets 
        ORDER BY id DESC LIMIT 5
    """).fetchall()
    conn.close()
    return render_template("index.html", departments=departments, categories=categories, recent_tickets=recent_tickets)

@app.route("/tiket/buat", methods=["POST"])
def submit_ticket():
    """Proses pembuatan tiket baru dari formulir pengguna"""
    reporter_name = request.form.get("reporter_name", "").strip()
    department = request.form.get("department", "").strip()
    location = request.form.get("location", "").strip()
    contact = request.form.get("contact", "").strip()
    category = request.form.get("category", "").strip()
    priority = request.form.get("priority", "Normal").strip()
    subject = request.form.get("subject", "").strip()
    description = request.form.get("description", "").strip()

    if not reporter_name or not department or not category or not subject or not description:
        flash("Mohon lengkapi semua bidang yang wajib diisi!", "danger")
        return redirect(url_for("index"))

    ticket_number = generate_ticket_number()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO tickets (ticket_number, reporter_name, department, location, contact, category, priority, subject, description, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Menunggu', ?, ?)
    """, (ticket_number, reporter_name, department, location, contact, category, priority, subject, description, now_str, now_str))
    conn.commit()
    conn.close()

    flash(f"Tiket berhasil dibuat dengan nomor: {ticket_number}", "success")
    return redirect(url_for("ticket_success", ticket_number=ticket_number))

@app.route("/tiket/sukses/<ticket_number>")
def ticket_success(ticket_number):
    """Halaman konfirmasi setelah tiket berhasil dibuat"""
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE ticket_number = ?", (ticket_number,)).fetchone()
    conn.close()
    if not ticket:
        flash("Tiket tidak ditemukan.", "warning")
        return redirect(url_for("index"))
    return render_template("ticket_success.html", ticket=ticket)

@app.route("/lacak", methods=["GET", "POST"])
def track_ticket():
    """Halaman pelacakan tiket oleh user menggunakan nomor tiket"""
    ticket = None
    searched_number = ""
    if request.method == "POST":
        searched_number = request.form.get("ticket_number", "").strip().upper()
    elif request.args.get("q"):
        searched_number = request.args.get("q", "").strip().upper()

    if searched_number:
        conn = get_db_connection()
        ticket = conn.execute("SELECT * FROM tickets WHERE ticket_number = ?", (searched_number,)).fetchone()
        conn.close()
        if not ticket:
            flash(f"Tiket dengan nomor '{searched_number}' tidak ditemukan.", "danger")

    return render_template("ticket_status.html", ticket=ticket, searched_number=searched_number)

@app.route("/it/dashboard")
def dashboard():
    """Dashboard Utama IT: Statistik Per Departemen & Kategori"""
    conn = get_db_connection()
    
    # Ringkasan KPI
    total_tickets = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    waiting_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Menunggu'").fetchone()[0]
    in_progress_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Sedang Dikerjakan'").fetchone()[0]
    resolved_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Selesai'").fetchone()[0]

    # Statistik Khusus PER DEPARTEMEN (Menjawab inti kebutuhan pengguna)
    dept_stats = conn.execute("""
        SELECT 
            department,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Menunggu' THEN 1 ELSE 0 END) as waiting,
            SUM(CASE WHEN status = 'Sedang Dikerjakan' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'Selesai' THEN 1 ELSE 0 END) as resolved
        FROM tickets
        GROUP BY department
        ORDER BY total DESC
    """).fetchall()

    # Statistik Kategori Masalah
    category_stats = conn.execute("""
        SELECT category, COUNT(*) as total 
        FROM tickets 
        GROUP BY category 
        ORDER BY total DESC
    """).fetchall()

    # Statistik Prioritas Masalah
    priority_stats = conn.execute("""
        SELECT priority, COUNT(*) as total 
        FROM tickets 
        GROUP BY priority
    """).fetchall()

    # 10 Tiket Terakhir untuk Action Cepat
    recent_tickets = conn.execute("""
        SELECT * FROM tickets ORDER BY id DESC LIMIT 10
    """).fetchall()

    conn.close()

    # Siapkan data untuk Chart.js (JSON-friendly)
    dept_labels = [row["department"] for row in dept_stats]
    dept_totals = [row["total"] for row in dept_stats]
    dept_waiting = [row["waiting"] for row in dept_stats]
    dept_inprogress = [row["in_progress"] for row in dept_stats]
    dept_resolved = [row["resolved"] for row in dept_stats]

    cat_labels = [row["category"] for row in category_stats]
    cat_totals = [row["total"] for row in category_stats]

    return render_template(
        "dashboard.html",
        total_tickets=total_tickets,
        waiting_tickets=waiting_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets,
        dept_stats=dept_stats,
        category_stats=category_stats,
        priority_stats=priority_stats,
        recent_tickets=recent_tickets,
        dept_labels=dept_labels,
        dept_totals=dept_totals,
        dept_waiting=dept_waiting,
        dept_inprogress=dept_inprogress,
        dept_resolved=dept_resolved,
        cat_labels=cat_labels,
        cat_totals=cat_totals
    )

@app.route("/it/tiket")
def ticket_list():
    """Halaman Daftar Semua Tiket dengan Filter Departemen & Status"""
    dept_filter = request.args.get("department", "").strip()
    status_filter = request.args.get("status", "").strip()
    category_filter = request.args.get("category", "").strip()
    search_query = request.args.get("search", "").strip()

    conn = get_db_connection()
    departments = conn.execute("SELECT * FROM departments ORDER BY name ASC").fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()

    sql = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if dept_filter:
        sql += " AND department = ?"
        params.append(dept_filter)
    if status_filter:
        sql += " AND status = ?"
        params.append(status_filter)
    if category_filter:
        sql += " AND category = ?"
        params.append(category_filter)
    if search_query:
        sql += " AND (ticket_number LIKE ? OR reporter_name LIKE ? OR subject LIKE ? OR description LIKE ?)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term, like_term])

    sql += " ORDER BY id DESC"
    tickets = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template(
        "tickets.html",
        tickets=tickets,
        departments=departments,
        categories=categories,
        dept_filter=dept_filter,
        status_filter=status_filter,
        category_filter=category_filter,
        search_query=search_query
    )

@app.route("/it/tiket/<int:ticket_id>", methods=["GET", "POST"])
def ticket_detail(ticket_id):
    """Detail Tiket & Update Status / Solusi oleh Tim IT"""
    conn = get_db_connection()
    
    if request.method == "POST":
        status = request.form.get("status", "").strip()
        technician = request.form.get("technician", "").strip()
        solution = request.form.get("solution", "").strip()
        priority = request.form.get("priority", "").strip()
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resolved_at = now_str if status == "Selesai" else None

        conn.execute("""
            UPDATE tickets
            SET status = ?, technician = ?, solution = ?, priority = ?, updated_at = ?,
                resolved_at = CASE WHEN ? = 'Selesai' THEN ? ELSE resolved_at END
            WHERE id = ?
        """, (status, technician, solution, priority, now_str, status, now_str, ticket_id))
        conn.commit()
        flash("Status tiket berhasil diperbarui!", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()

    if not ticket:
        flash("Tiket tidak ditemukan.", "danger")
        return redirect(url_for("ticket_list"))

    return render_template("ticket_detail.html", ticket=ticket)

@app.route("/it/tiket/hapus/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    """Hapus tiket"""
    conn = get_db_connection()
    conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    flash("Tiket berhasil dihapus.", "info")
    return redirect(url_for("ticket_list"))

@app.route("/it/departemen")
def department_analytics():
    """Halaman Khusus Analisis Rinci Troubleshooting per Departemen"""
    conn = get_db_connection()
    
    # Rekap per Departemen lengkap dengan detail trouble yang sering terjadi
    dept_records = conn.execute("""
        SELECT 
            department,
            COUNT(*) as total_trouble,
            SUM(CASE WHEN status = 'Menunggu' THEN 1 ELSE 0 END) as open_trouble,
            SUM(CASE WHEN status = 'Sedang Dikerjakan' THEN 1 ELSE 0 END) as ongoing_trouble,
            SUM(CASE WHEN status = 'Selesai' THEN 1 ELSE 0 END) as fixed_trouble,
            MAX(created_at) as last_reported
        FROM tickets
        GROUP BY department
        ORDER BY total_trouble DESC
    """).fetchall()

    # Rincian departemen x kategori masalah
    dept_cat_matrix = conn.execute("""
        SELECT department, category, COUNT(*) as count
        FROM tickets
        GROUP BY department, category
        ORDER BY department, count DESC
    """).fetchall()

    conn.close()

    # Format data matriks per departemen
    dept_issues = {}
    for row in dept_cat_matrix:
        d = row["department"]
        if d not in dept_issues:
            dept_issues[d] = []
        dept_issues[d].append(f"{row['category']} ({row['count']}x)")

    return render_template("departments.html", dept_records=dept_records, dept_issues=dept_issues)

@app.route("/it/pengaturan", methods=["GET", "POST"])
def settings():
    """Pengaturan Master Departemen & Kategori"""
    conn = get_db_connection()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_dept":
            dept_name = request.form.get("dept_name", "").strip()
            desc = request.form.get("dept_desc", "").strip()
            if dept_name:
                try:
                    conn.execute("INSERT INTO departments (name, description) VALUES (?, ?)", (dept_name, desc))
                    conn.commit()
                    flash(f"Departemen '{dept_name}' berhasil ditambahkan.", "success")
                except Exception:
                    flash(f"Departemen '{dept_name}' sudah ada.", "warning")
        elif action == "delete_dept":
            dept_id = request.form.get("dept_id")
            conn.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
            conn.commit()
            flash("Departemen berhasil dihapus.", "info")
        elif action == "add_cat":
            cat_name = request.form.get("cat_name", "").strip()
            desc = request.form.get("cat_desc", "").strip()
            if cat_name:
                try:
                    conn.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (cat_name, desc))
                    conn.commit()
                    flash(f"Kategori '{cat_name}' berhasil ditambahkan.", "success")
                except Exception:
                    flash(f"Kategori '{cat_name}' sudah ada.", "warning")
        elif action == "delete_cat":
            cat_id = request.form.get("cat_id")
            conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
            conn.commit()
            flash("Kategori berhasil dihapus.", "info")

    departments = conn.execute("SELECT * FROM departments ORDER BY name ASC").fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
    conn.close()

    return render_template("settings.html", departments=departments, categories=categories)

@app.route("/it/export/excel")
def export_excel():
    """Ekspor seluruh data tiket dan rekap per departemen ke format Excel (.xlsx)"""
    conn = get_db_connection()
    df_tickets = pd.read_sql_query("""
        SELECT 
            ticket_number AS 'No Tiket',
            created_at AS 'Waktu Lapor',
            reporter_name AS 'Pelapor',
            department AS 'Departemen',
            location AS 'Lokasi',
            contact AS 'Kontak',
            category AS 'Kategori Gangguan',
            priority AS 'Prioritas',
            subject AS 'Judul Masalah',
            description AS 'Deskripsi Kendala',
            status AS 'Status',
            technician AS 'Teknisi IT',
            solution AS 'Solusi / Tindakan',
            resolved_at AS 'Waktu Selesai'
        FROM tickets
        ORDER BY id DESC
    """, conn)

    df_dept_summary = pd.read_sql_query("""
        SELECT 
            department AS 'Departemen',
            COUNT(*) AS 'Total Tiket Masuk',
            SUM(CASE WHEN status = 'Menunggu' THEN 1 ELSE 0 END) AS 'Menunggu (Open)',
            SUM(CASE WHEN status = 'Sedang Dikerjakan' THEN 1 ELSE 0 END) AS 'Diproses',
            SUM(CASE WHEN status = 'Selesai' THEN 1 ELSE 0 END) AS 'Selesai Ditangani'
        FROM tickets
        GROUP BY department
        ORDER BY COUNT(*) DESC
    """, conn)
    conn.close()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_dept_summary.to_excel(writer, sheet_name='Rekap Per Departemen', index=False)
        df_tickets.to_excel(writer, sheet_name='Daftar Seluruh Tiket', index=False)

    output.seek(0)
    filename = f"Laporan_Tiket_IT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        download_name=filename,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    # Host 0.0.0.0 memungkinkan diakses oleh komputer lain di jaringan LAN kantor
    app.run(host="0.0.0.0", port=5000, debug=True)
