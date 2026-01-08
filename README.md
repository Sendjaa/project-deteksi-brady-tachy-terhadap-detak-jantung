# project-deteksi-brady-tachy-terhadap-detak-jantung
sistem monitoring detak jantung real-time menggunakan Raspberry Pi, Flask, dan Socket.io. Sistem ini mendeteksi kondisi anomali seperti Tachycardia dan Bradycardia dan menampilkannya secara instan di dashboard web tanpa perlu memuat ulang halaman.

Fitur Utama
Real-time Updates: Menggunakan WebSocket (Socket.io) untuk pengiriman data instan.
Automated Logging: Mencatat peringatan (warning) secara otomatis ke dalam tabel sesi.
Filtering: Memungkinkan pengguna menyaring jenis peringatan tertentu.
Responsive Design: Tampilan bersih menggunakan Tailwind CSS.

Persyaratan Sistem
Hardware: Raspberry Pi (3/4/5 atau Zero W).
OS: Raspberry Pi OS (atau Linux lainnya).
Language: Python 3.x.
Libraries: Flask, Flask-SocketIO, Eventlet.

Struktur Folder
monitoring-jantung/
├── app.py              # Server Flask (Backend)
├── templates/
│   ├── base.html       # Template utama (layout)
│   └── logs.html       # Halaman log peringatan (Frontend)
└── README.md           # Dokumentasi proyek

Instalasi
1. Clone atau Masuk ke Folder Proyek:
mkdir monitoring-jantung
cd monitoring-jantung

2. Instal Dependensi: Jalankan perintah berikut di terminal Raspberry Pi:
pip install flask flask-socketio eventlet

3. Siapkan File:
Simpan kode Python ke dalam app.py.
Simpan kode HTML Anda ke dalam templates/logs.html.

4. Cara MenjalankanJalankan server Python:
python3 app.py

Akses Dashboard:
Buka browser dan ketik alamat berikut:Lokal (di Pi): 
http://127.0.0.1:5000

Perangkat Lain (WiFi yang sama): 
http://[IP-RASPBERRY-PI]:5000(Gunakan perintah hostname -I untuk mengetahui IP Raspberry Pi).

📊 Logika Peringatan (Warning)Sistem dikonfigurasi untuk mencatat log hanya jika kondisi TIDAK NORMAL:
Kondisi,Detak Jantung (BPM),Status di Log
Normal,60−100 BPM,Tidak dicatat
Tachycardia,>100 BPM,Critical
Bradycardia,<60 BPM,Critical

Catatan Penting
Log Temporer: Karena tidak menggunakan database, data log di tabel akan hilang jika halaman web di-refresh atau browser ditutup.
Transports: Menggunakan transports: ['websocket'] pada sisi klien untuk performa terbaik di Raspberry Pi.
