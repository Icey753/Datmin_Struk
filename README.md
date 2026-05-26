# Data Mining Receipt

Repositori ini berisi pipeline data mining untuk struk belanja dari Super Indo, Alfamart, dan Indomaret. Data produk diekstrak dari PDF/gambar struk, digabungkan, dikategorikan secara rule-based, lalu dianalisis menggunakan association rule mining dengan Apriori dan FP-Growth.

## Ringkasan Pipeline

1. Ekstraksi produk dari struk Super Indo PDF menggunakan Python.
2. Ekstraksi produk dari gambar struk Alfamart dan Indomaret menggunakan Windows OCR.
3. Penggabungan semua hasil ekstraksi ke satu dataset transaksi.
4. Kategorisasi produk berdasarkan keyword.
5. Analisis asosiasi kategori belanja dengan Apriori manual, Apriori `arules`, dan FP-Growth.
6. Ekspor hasil analisis ke Excel, CSV, PNG, dan dokumen laporan.

## Struktur Repo

```text
datmin receipt/
|-- tes.py                              # Ekstraksi struk Super Indo dari PDF
|-- tes2.py                             # Ekstraksi struk Alfamart dari gambar/OCR
|-- tes3.py                             # Ekstraksi struk Indomaret dari gambar/OCR
|-- merge.py                            # Menggabungkan hasil ekstraksi
|-- kategorisasi.py                     # Kategorisasi produk rule-based
|-- analisis_asosiasi_input_manual.R    # Analisis asosiasi dan visualisasi dengan R
|-- Rmd analisis.Rmd                    # Versi R Markdown analisis
|
|-- alfamaret/                          # Gambar struk Alfamart
|-- indomaret/                          # Gambar struk Indomaret
|-- E-Receipt_*.pdf                     # PDF struk Super Indo
|-- E-Reciept_*.pdf                     # PDF struk Super Indo dengan variasi nama file
|
|-- hasil_barang_alfamaret.xlsx         # Output ekstraksi Alfamart
|-- hasil_barang_indomaret.xlsx         # Output ekstraksi Indomaret
|-- hasil_barang_receipt.xlsx           # Output ekstraksi Super Indo
|-- hasil_gabungan.xlsx                 # Dataset gabungan semua sumber
|-- hasil_kategorisasi.xlsx             # Dataset final dengan kategori
|
|-- rules_apriori_manual.csv            # Rules hasil Apriori manual
|-- rules_apriori_arules.csv            # Rules hasil Apriori dari package arules
|-- rules_fpgrowth.csv                  # Rules hasil FP-Growth/ruleInduction
|-- rules_apriori_kategori.csv          # Output rules kategori tambahan
|-- rules_fpgrowth_kategori.csv         # Output rules kategori tambahan
|
|-- viz_01_frekuensi_kategori.png       # Visualisasi frekuensi kategori
|-- viz_02_graph_apriori.png            # Graph rules Apriori
|-- viz_03_graph_fpgrowth.png           # Graph rules FP-Growth
|-- viz_04_perbandingan_metode.png      # Perbandingan jumlah rules
|-- viz_05_perbandingan_metode.png      # Visualisasi perbandingan tambahan
|-- analisis_apriori_fpgrowth.docx      # Dokumen hasil analisis
|-- README.md
```

## Requirements

Python:

```bash
pip install pandas openpyxl pdfplumber
```

R:

```r
install.packages(c(
  "arules", "arulesViz", "dplyr", "tidyr",
  "ggplot2", "stringr", "RColorBrewer"
))
```

Catatan:

- `tes2.py` dan `tes3.py` memakai Windows OCR, sehingga paling cocok dijalankan di Windows 10/11.
- Nama folder `alfamaret` mengikuti nama folder yang ada di repo.

## Cara Menjalankan

### 1. Ekstraksi Struk

```bash
python tes.py
python tes2.py
python tes3.py
```

Detail input dan output:

| Script | Sumber | Input Default | Output |
| --- | --- | --- | --- |
| `tes.py` | Super Indo | PDF di root repo | `hasil_barang_receipt.xlsx` |
| `tes2.py` | Alfamart | Gambar di `alfamaret/` | `hasil_barang_alfamaret.xlsx` |
| `tes3.py` | Indomaret | Gambar di `indomaret/` | `hasil_barang_indomaret.xlsx` |

Setiap file output ekstraksi berisi kolom:

| Kolom | Keterangan |
| --- | --- |
| `struk_ke` | Nomor urut struk pada sumber masing-masing |
| `tanggal_transaksi` | Tanggal transaksi |
| `nama_barang` | Nama produk hasil ekstraksi |

### 2. Gabungkan Data

```bash
python merge.py
```

`merge.py` membaca tiga file hasil ekstraksi, menambahkan kolom `sumber`, mengurutkan transaksi berdasarkan tanggal, lalu membuat ulang `struk_ke` secara global.

Output: `hasil_gabungan.xlsx`

| Kolom | Keterangan |
| --- | --- |
| `struk_ke` | Nomor transaksi global |
| `sumber` | Asal data: Alfamaret, Indomaret, atau SuperIndo |
| `tanggal_transaksi` | Tanggal transaksi |
| `nama_barang` | Nama produk |

### 3. Kategorisasi Produk

```bash
python kategorisasi.py
```

`kategorisasi.py` membaca `hasil_gabungan.xlsx`, mencocokkan `nama_barang` dengan daftar keyword, lalu menambahkan kolom `kategori`.

Output: `hasil_kategorisasi.xlsx`

Kategori yang dipakai saat ini:

| No | Kategori |
| --- | --- |
| 1 | Bahan Pokok |
| 2 | Bumbu & Rempah |
| 3 | Sayuran |
| 4 | Buah |
| 5 | Daging & Olahan |
| 6 | Ikan & Seafood |
| 7 | Frozen Food |
| 8 | Susu & Olahan Susu |
| 9 | Mie Instan |
| 10 | Snack |
| 11 | Makanan Instan |
| 12 | Roti |
| 13 | Minuman |
| 14 | Kebersihan Rumah |
| 15 | Kantong & Tas |
| 16 | Perawatan Tubuh |

Metode kategorisasi bersifat rule-based:

- Keyword dicocokkan secara case-insensitive.
- Rule pertama yang cocok menjadi kategori produk.
- Produk yang tidak cocok masuk kategori `Lainnya`.
- Pada dataset terbaru, tidak ada produk yang masuk `Lainnya`.

### 4. Analisis Asosiasi

Jalankan script R:

```bash
Rscript analisis_asosiasi_input_manual.R
```

Atau buka `Rmd analisis.Rmd` di RStudio untuk menjalankan analisis dalam format notebook/report.

Analisis menggunakan transaksi kategori `T1` sampai `T31` dengan parameter:

| Parameter | Nilai |
| --- | --- |
| Jumlah transaksi | 31 |
| `PHI` / minimum support count | 3 |
| `MIN_CONF` | 0.5 |
| `MIN_LIFT` | 1.0 |
| Periode data | 2024-06-08 sampai 2026-05-25 |

Output utama:

| File | Keterangan |
| --- | --- |
| `rules_apriori_manual.csv` | Association rules dari implementasi Apriori manual |
| `rules_apriori_arules.csv` | Association rules dari package `arules` |
| `rules_fpgrowth.csv` | Association rules dari frequent itemset mining dan `ruleInduction` |
| `viz_01_frekuensi_kategori.png` | Frekuensi kategori per transaksi |
| `viz_02_graph_apriori.png` | Graph rules Apriori |
| `viz_03_graph_fpgrowth.png` | Graph rules FP-Growth |
| `viz_04_perbandingan_metode.png` | Perbandingan jumlah rules tiap metode |

## Statistik Dataset Terbaru

Statistik berikut dibaca dari file output yang ada di repo saat ini.

| File | Baris | Struk | Rentang Tanggal |
| --- | ---: | ---: | --- |
| `hasil_barang_alfamaret.xlsx` | 28 | 8 | 2026-02-28 sampai 2026-05-12 |
| `hasil_barang_indomaret.xlsx` | 45 | 7 | 2026-03-03 sampai 2026-05-25 |
| `hasil_barang_receipt.xlsx` | 121 | 16 | 2024-06-08 sampai 2026-03-13 |
| `hasil_gabungan.xlsx` | 194 | 31 | 2024-06-08 sampai 2026-05-25 |
| `hasil_kategorisasi.xlsx` | 194 | 31 | 2024-06-08 sampai 2026-05-25 |

Ringkasan final:

| Metrik | Nilai |
| --- | ---: |
| Total baris final | 194 |
| Total struk final | 31 |
| Produk unik | 173 |
| Kategori terpakai | 16 |
| Produk kategori `Lainnya` | 0 |
| Rules Apriori manual | 24 |
| Rules Apriori `arules` | 24 |
| Rules FP-Growth | 24 |

Distribusi kategori pada `hasil_kategorisasi.xlsx`:

| Kategori | Jumlah |
| --- | ---: |
| Snack | 24 |
| Bahan Pokok | 23 |
| Bumbu & Rempah | 23 |
| Minuman | 18 |
| Perawatan Tubuh | 17 |
| Sayuran | 15 |
| Susu & Olahan Susu | 14 |
| Frozen Food | 10 |
| Kantong & Tas | 9 |
| Mie Instan | 9 |
| Daging & Olahan | 9 |
| Buah | 7 |
| Kebersihan Rumah | 5 |
| Makanan Instan | 5 |
| Ikan & Seafood | 4 |
| Roti | 2 |

## Pipeline Lengkap

```bash
# Ekstraksi
python tes.py
python tes2.py
python tes3.py

# Transformasi dataset
python merge.py
python kategorisasi.py

# Analisis asosiasi
Rscript analisis_asosiasi_input_manual.R
```

File akhir yang paling penting:

- `hasil_kategorisasi.xlsx` untuk dataset transaksi produk dan kategori.
- `rules_apriori_manual.csv`, `rules_apriori_arules.csv`, dan `rules_fpgrowth.csv` untuk hasil association rules.
- `viz_*.png` untuk visualisasi.
- `analisis_apriori_fpgrowth.docx` untuk dokumen laporan analisis.
