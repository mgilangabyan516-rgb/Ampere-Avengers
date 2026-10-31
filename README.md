# AquaDrain-AI MVP

Software prototipe untuk demonstrasi pemantauan tekanan/debit dan klasifikasi indikasi kebocoran.

## Isi folder
- `app.py`: dashboard Streamlit (simulasi, unggah CSV, riwayat).
- `model.py`: Random Forest demonstrasi dan data sintetis.
- `api.py`: API FastAPI untuk menerima data ESP32.
- `storage.py`: penyimpanan lokal SQLite.
- `esp32_aquadrain.ino`: contoh firmware ESP32 (perlu penyesuaian sensor).

## 1. Instalasi
Disarankan Python 3.10 atau lebih baru.

Buka terminal di folder proyek, lalu:
```bash
python -m venv .venv
```
Windows:
```bash
.venv\Scripts\activate
```
Mac/Linux:
```bash
source .venv/bin/activate
```
Kemudian:
```bash
pip install -r requirements.txt
```

## 2. Jalankan dashboard
```bash
streamlit run app.py
```
Browser akan membuka dashboard AquaDrain-AI. Mulai dengan mode "Simulasi manual".

## 3. Jalankan API untuk ESP32
Buka terminal kedua pada folder proyek:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
Cari alamat IP laptop pada jaringan Wi-Fi yang sama. Ubah `SERVER_URL` di `esp32_aquadrain.ino` menjadi:
`http://IP-LAPTOP:8000/sensor`

Upload sketch ke ESP32. Dashboard dan API harus berjalan pada jaringan yang sama. Pastikan firewall laptop mengizinkan koneksi lokal ke port 8000.

## 4. Format CSV
Kolom wajib:
- `pressure_1`
- `pressure_2`
- `flow_1`
- `flow_2`
- `pump_status` (0=OFF, 1=ON)

Kolom `timestamp` opsional. Gunakan satuan yang konsisten: contoh tekanan bar dan debit L/min.

Contoh:
```csv
timestamp,pressure_1,pressure_2,flow_1,flow_2,pump_status
2026-10-30T10:00:00,2.8,2.7,8.0,7.9,1
2026-10-30T10:00:02,2.8,2.1,8.0,6.4,1
```

## PENTING: batasan dan keselamatan
1. Model Random Forest bawaan dilatih dari data SINTETIS agar alur aplikasi bisa didemonstrasikan. Metrik yang tampil bukan hasil validasi lapangan dan tidak boleh diklaim sebagai akurasi produk.
2. Untuk penggunaan nyata, kumpulkan dataset eksperimen berlabel normal/bocor, kalibrasi sensor, pisahkan data train/test berdasarkan sesi eksperimen, lalu latih dan validasi model dengan data nyata.
3. Threshold status NORMAL/WARNING/LEAK SUSPECTED adalah nilai demonstrasi yang perlu dituning.
4. Rumus konversi sensor di sketch ESP32 adalah placeholder. Wajib disesuaikan dengan datasheet, rentang tegangan, dan hasil kalibrasi sensor yang dibeli.
5. Jangan hubungkan output sensor 5V langsung ke pin ESP32 3.3V. Gunakan rangkaian penyesuai tegangan yang sesuai. Jaga perangkat listrik tetap terpisah dari air, gunakan catu daya tegangan rendah yang sesuai, dan minta bantuan pembimbing/teknisi saat merakit.
6. Versi ini menyimpan data pada SQLite lokal. Belum menggunakan layanan cloud publik, autentikasi, enkripsi transport tingkat produksi, atau kontrol katup otomatis.
