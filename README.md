#  Data Mining — Ekstraksi & Kategorisasi Struk Belanja

Proyek ini mengekstrak data produk dari struk belanja **Super Indo**, **Alfamart**, dan **Indomaret**, lalu menggabungkan dan mengkategorisasikan seluruh data menjadi satu dataset terstruktur dalam format Excel.

---

##  Struktur Proyek

```
datmin receipt/
│
├── tes.py                          # Ekstraksi struk Super Indo (PDF)
├── tes2.py                         # Ekstraksi struk Alfamart (gambar/OCR)
├── tes3.py                         # Ekstraksi struk Indomaret (gambar/OCR)
├── merge.py                        # Penggabungan 3 file hasil → 1 file
├── kategorisasi.py                 # Kategorisasi rule-based
│
├── alfamaret/                      # Folder gambar struk Alfamart
├── indomaret/                      # Folder gambar struk Indomaret
├── E-Receipt_*.pdf                 # File PDF struk Super Indo
├── E-Reciept_*.pdf                 # File PDF struk Super Indo (varian nama)
│
├── hasil_barang_alfamaret.xlsx     # Output: data produk Alfamart
├── hasil_barang_indomaret.xlsx     # Output: data produk Indomaret
├── hasil_barang_receipt.xlsx       # Output: data produk Super Indo
├── hasil_gabungan.xlsx             # Output: gabungan 3 sumber
├── hasil_kategorisasi.xlsx         # Output: data final + kategori
│
└── README.md
```

---

##  Requirements

- **Python 3.10+**
- Library Python:
  ```
  pip install pandas openpyxl pdfplumber
  ```
- **Windows OCR** (untuk `tes2.py` dan `tes3.py`) — sudah tersedia bawaan di Windows 10/11

---

##  Cara Penggunaan

### 1. Ekstraksi Data dari Struk

Jalankan masing-masing script sesuai sumber data:

| Script     | Sumber Data       | Input                        | Output                         |
|------------|-------------------|------------------------------|--------------------------------|
| `tes.py`   | Super Indo (PDF)  | File PDF di folder root      | `hasil_barang_receipt.xlsx`    |
| `tes2.py`  | Alfamart (gambar) | Gambar di folder `alfamaret` | `hasil_barang_alfamaret.xlsx`  |
| `tes3.py`  | Indomaret (gambar)| Gambar di folder `indomaret` | `hasil_barang_indomaret.xlsx`  |

```bash
# Ekstraksi struk Super Indo (PDF)
python tes.py

# Ekstraksi struk Alfamart (gambar, pakai Windows OCR)
python tes2.py

# Ekstraksi struk Indomaret (gambar, pakai Windows OCR)
python tes3.py
```

Setiap script menghasilkan file Excel dengan 3 kolom:

| Kolom               | Keterangan                          |
|----------------------|-------------------------------------|
| `struk_ke`           | Nomor urut struk (per sumber)       |
| `tanggal_transaksi`  | Tanggal transaksi (YYYY-MM-DD)      |
| `nama_barang`        | Nama produk yang dibeli             |

---

### 2. Penggabungan Data (`merge.py`)

Menggabungkan ketiga file hasil ekstraksi menjadi satu file `hasil_gabungan.xlsx`.

```bash
python merge.py
```

**Yang dilakukan `merge.py`:**
- Membaca `hasil_barang_alfamaret.xlsx`, `hasil_barang_indomaret.xlsx`, dan `hasil_barang_receipt.xlsx`
- Menambahkan kolom `sumber` (Alfamaret / Indomaret / SuperIndo)
- Mengurutkan data berdasarkan `tanggal_transaksi` (terlama → terbaru)
- Me-renumber `struk_ke` secara global (1, 2, 3, ... tanpa duplikat antar sumber)

**Output `hasil_gabungan.xlsx`:**

| Kolom               | Keterangan                            |
|----------------------|---------------------------------------|
| `struk_ke`           | Nomor urut struk global (1–31)        |
| `sumber`             | Asal data (Alfamaret/Indomaret/SuperIndo) |
| `tanggal_transaksi`  | Tanggal transaksi (YYYY-MM-DD)        |
| `nama_barang`        | Nama produk yang dibeli               |

---

### 3. Kategorisasi (`kategorisasi.py`)

Mengkategorisasikan setiap produk menggunakan metode **rule-based** (keyword matching).

```bash
python kategorisasi.py
```

**Yang dilakukan `kategorisasi.py`:**
- Membaca `hasil_gabungan.xlsx`
- Mencocokkan `nama_barang` dengan daftar keyword per kategori
- Menambahkan kolom `kategori`
- Menyimpan ke `hasil_kategorisasi.xlsx`

**Daftar 19 Kategori:**

| No | Kategori            | Contoh Produk                         |
|----|---------------------|---------------------------------------|
| 1  | Bahan Pokok         | Beras, Gula, Minyak Goreng, Telur     |
| 2  | Bumbu & Rempah      | Bawang, Cabe, Masako, Kecap           |
| 3  | Sayuran             | Bayam, Kangkung, Wortel, Tomat        |
| 4  | Buah                | Mangga, Nanas, Anggur, Lemon          |
| 5  | Daging & Olahan     | Daging Ayam, Bakso, Tempe             |
| 6  | Ikan & Seafood      | Ikan Kembung, Cumi, Udang             |
| 7  | Frozen Food         | Nugget, Hato, Belfoods                |
| 8  | Susu & Olahan Susu  | Indomilk, Frisian, Cimory             |
| 9  | Mie Instan          | Indomie, Pop Mie, Sedaap              |
| 10 | Makanan Instan      | Super Bubur, Energen, Nutrijell       |
| 11 | Snack               | Biskuat, Tango, Chiki, Kusuka         |
| 12 | Roti                | Mr. Bread                             |
| 13 | Minuman             | Teh, Kopi, You C, Aqua                |
| 14 | Kebersihan Rumah    | Sunlight, HIT, Tissue                 |
| 15 | Kantong & Tas       | Reusable Bag, Kantong Plastik         |
| 16 | Perawatan Tubuh     | Shampoo, Sabun, Deodorant, Pasta Gigi |
| 17 | Popok & Pembalut    | Mamy Poko, Charm                      |
| 18 | Rokok               | Various brands                        |
| 19 | Obat & Kesehatan    | Obat-obatan                           |

---

## Pipeline Lengkap

Untuk menjalankan seluruh proses dari awal sampai akhir:

```bash
# Step 1: Ekstraksi data dari masing-masing sumber
python tes.py       # Super Indo (PDF)
python tes2.py      # Alfamart (gambar)
python tes3.py      # Indomaret (gambar)

# Step 2: Gabungkan semua data
python merge.py

# Step 3: Kategorisasi
python kategorisasi.py
```

**Hasil akhir** ada di `hasil_kategorisasi.xlsx` dengan kolom:
`struk_ke` | `sumber` | `tanggal_transaksi` | `nama_barang` | `kategori`

---

##  Statistik Dataset

| Metrik             | Nilai                       |
|--------------------|-----------------------------|
| Total baris        | 194                         |
| Total struk        | 31                          |
| Rentang tanggal    | 2024-06-08 s/d 2026-05-25   |
| Sumber data        | Super Indo, Alfamart, Indomaret |
| Jumlah kategori    | 19                          |
| Produk unik        | 173                         |

---

## Metode Kategorisasi

Proyek ini menggunakan pendekatan **rule-based classification** (bukan machine learning):

1. **Definisi Rules** — Setiap kategori memiliki daftar keyword yang merepresentasikan produk-produk di kategori tersebut.
2. **Keyword Matching** — Untuk setiap `nama_barang`, dicek apakah mengandung salah satu keyword dari setiap rule (case-insensitive).
3. **First Match Wins** — Rule yang pertama kali cocok akan menentukan kategori. Rules yang lebih spesifik ditempatkan lebih dahulu.
4. **Fallback** — Jika tidak ada rule yang cocok, produk masuk kategori "Lainnya".

### Kelebihan Rule-Based vs Decision Tree:
- **Transparan** — Bisa langsung dilihat kenapa suatu produk masuk kategori tertentu
- **Mudah di-maintain** — Tinggal tambah keyword jika ada produk baru
- **Tidak butuh training data** — Cocok untuk dataset kecil
- **Akurasi tinggi** — 100% produk berhasil dikategorisasikan (0 masuk "Lainnya")
