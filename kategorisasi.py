"""Kategorisasi rule-based untuk hasil_gabungan.xlsx."""

import os
import re
import pandas as pd


INPUT  = "hasil_gabungan.xlsx"
OUTPUT = "hasil_kategorisasi.xlsx"


RULES: list[tuple[list[str], str]] = [

    (["BERAS", "TOPI KOKI"], "Bahan Pokok"),
    (["GULA", "GULAKU", "R/B GULA"], "Bahan Pokok"),
    (["MINYAK", "BIMOLI", "SUNCO", "TROPICAL"], "Bahan Pokok"),
    (["TELUR", "TLR"], "Bahan Pokok"),
    (["TEPUNG", "SAJIKU"], "Bahan Pokok"),
    (["SANTAN", "SUN KARA"], "Bahan Pokok"),
    (["BLUE BAND"], "Bahan Pokok"),

    (["BAWANG MERAH", "BAWANG PUTIH"], "Bumbu & Rempah"),
    (["CABE", "CABAI"], "Bumbu & Rempah"),
    (["LENGKUAS", "LAOS"], "Bumbu & Rempah"),
    (["DAUN JERUK", "DAUN BAWANG"], "Bumbu & Rempah"),
    (["JINTEN", "KAPULAGA", "KAYU MANIS", "BIJI PALA", "BUNGA LAWANG", "ADAS"], "Bumbu & Rempah"),
    (["TERASI"], "Bumbu & Rempah"),
    (["MASAKO", "ROYCO", "TOTOLE", "KALDU"], "Bumbu & Rempah"),
    (["KECAP", "KCPMNS", "KECAP MNS"], "Bumbu & Rempah"),
    (["SAUS", "S/TIRAM", "SAUS TIRAM", "SAMBAL", "MAESTRO"], "Bumbu & Rempah"),
    (["INDOFOOD B/R", "INDOFOOD SMB"], "Bumbu & Rempah"),

    (["BAYAM", "KANGKUNG", "CAISIM", "SAWI"], "Sayuran"),
    (["WORTEL", "TOMAT", "TERONG", "BANGKUANG"], "Sayuran"),
    (["JAGUNG MANIS"], "Sayuran"),

    (["MANGGA", "NANAS", "ANGGUR", "JAMBU", "LEMON IMPORT", "PEAR"], "Buah"),

    (["DAGING", "BAKSO"], "Daging & Olahan"),
    (["IKAN", "CUMI", "UDANG", "R/LAUT"], "Ikan & Seafood"),
    (["TEMPE"], "Daging & Olahan"),

    (["NUGGET", "HATO", "BELFOODS", "NUG"], "Frozen Food"),

    (["INDOMILK", "FRISIAN", "CIMORY", "OVALTINE"], "Susu & Olahan Susu"),
    (["OATSIDE"], "Susu & Olahan Susu"),

    (["INDOMIE", "POP MIE", "MI GEMEZ", "SEDAAP MIE", "SDP MI", "SOTO MI", "IDM M/GORENG"], "Mie Instan"),

    (["BISKUAT", "ROMA", "TANGO", "MONDE", "A.T.B MARIE"], "Snack"),
    (["CHIKI", "KUSUKA", "KRAKER", "LRSST PILUS", "TOS TOS", "CRUNCHY"], "Snack"),
    (["CHOKI CHOKI", "LOTTE", "SERENA", "GERY"], "Snack"),
    (["MR.POTATO", "NABATI"], "Snack"),
    (["S/Q CHOCO", "SQ BT", "SQ CHK", "SQ CK", "SQ CSW", "CAMPINA"], "Snack"),
    (["SUPER BUBUR"], "Makanan Instan"),
    (["ENERGEN"], "Makanan Instan"),
    (["NUTRIJEL", "NUTRIJELL"], "Makanan Instan"),

    (["MR. BREAD", "MY/R ROTI", "ROTI"], "Roti"),

    (["AQUA", "AQU"], "Minuman"),
    (["TEH", "SARIWANGI", "SOSRO", "ULTRA TEH"], "Minuman"),
    (["KOPI", "NESCAFE", "TOP/COFF", "TIC KPI"], "Minuman"),
    (["YOU C", "AMUNIZER", "NIPIS MADU"], "Minuman"),
    (["MARJAN"], "Minuman"),
    (["C/PANDA", "FOREST GRP"], "Minuman"),
    (["LEMNRL"], "Minuman"),
    (["FITMEUP"], "Minuman"),
    (["G/D INVNL", "LATT"], "Minuman"),

    (["SUNLIGHT", "SNLIGHT", "G/GEN DET", "DETERJEN"], "Kebersihan Rumah"),
    (["HIT XPRES", "HIT"], "Kebersihan Rumah"),
    (["TISSU", "TISSUE", "FACIAL TISSUE", "NICE SOFT", "IDM FAC"], "Kebersihan Rumah"),
    (["KANTONG PLASTIK", "IDM KTG PLSTK", "REUSABLE", "TAS IDUL", "ALFA ECO", "IDM FIT"], "Kantong & Tas"),

    (["SHAMPOO", "SHP", "PANTENE", "H&S"], "Perawatan Tubuh"),
    (["SABUN", "LUX BW", "BIORE", "NUVO", "CUSSONS"], "Perawatan Tubuh"),
    (["DEO", "REXONA", "RXONA", "POSH DEO", "NIVEA DEO"], "Perawatan Tubuh"),
    (["PEPSODENT"], "Perawatan Tubuh"),
    (["MARINA EDT"], "Perawatan Tubuh"),
    (["POND", "F/C ROOL"], "Perawatan Tubuh"),
    (["HERBORIST"], "Perawatan Tubuh"),
    (["S/PELL BABY", "SOFTENER"], "Perawatan Tubuh"),

    (["MAMY", "CHARM"], "Popok & Pembalut"),

    (["KNZLR", "SUKYNCK", "ROYAL SS"], "Rokok"),
    (["SUNBBR"], "Obat & Kesehatan"),
    (["CASAB", "COL FANT"], "Minuman"),
    (["SELECT BLT"], "Snack"),
]


def kategorisasi(nama_barang: str) -> str:
    upper = nama_barang.upper()
    for keywords, kategori in RULES:
        for kw in keywords:
            if kw.upper() in upper:
                return kategori
    return "Lainnya"


def main():
    if not os.path.exists(INPUT):
        print(f"[ERROR] File {INPUT} tidak ditemukan.")
        return

    print(f"Membaca {INPUT}...")
    df = pd.read_excel(INPUT)
    print(f"  Total baris: {len(df)}")

    print("Menerapkan kategorisasi rule-based...")
    df["tanggal_transaksi"] = pd.to_datetime(df["tanggal_transaksi"], errors="coerce").dt.date
    df["kategori"] = df["nama_barang"].apply(kategorisasi)

    print("\n=== DISTRIBUSI KATEGORI ===")
    dist = df["kategori"].value_counts()
    for kat, count in dist.items():
        print(f"  {kat:<25} : {count:>4} barang")
    print(f"  {'TOTAL':<25} : {len(df):>4} barang")

    lainnya = df[df["kategori"] == "Lainnya"]
    if len(lainnya) > 0:
        print(f"\n[PERINGATAN] {len(lainnya)} barang masuk 'Lainnya':")
        for nama in lainnya["nama_barang"].unique():
            print(f"  - {nama}")

    df.to_excel(OUTPUT, index=False, engine="openpyxl")
    print(f"\nFile berhasil disimpan: {OUTPUT}")


if __name__ == "__main__":
    main()
