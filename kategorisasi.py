"""Kategorisasi rule-based untuk hasil_gabungan.xlsx."""

import os
import re
import pandas as pd


INPUT  = "hasil_gabungan.xlsx"
OUTPUT = "hasil_kategorisasi.xlsx"


RULES: list[tuple[list[str], str]] = [

(["BERAS", "TOPI KOKI", "GULA", "GULAKU", "R/B GULA","R/LAUT", "MINYAK", "BIMOLI", "SUNCO", "TROPICAL", "TELUR", "TLR", "TEPUNG", "SAJIKU", "SANTAN", "SUN KARA", "BLUE BAND"], "Bahan Pokok"),

(["BAWANG MERAH", "BAWANG PUTIH", "CABE", "CABAI", "LENGKUAS", "LAOS", "DAUN JERUK", "DAUN BAWANG", "JINTEN", "KAPULAGA", "KAYU MANIS", "BIJI PALA", "BUNGA LAWANG", "ADAS", "TERASI", "MASAKO", "ROYCO", "TOTOLE", "KALDU", "KECAP", "KCPMNS", "KECAP MNS", "SAUS", "S/TIRAM", "SAUS TIRAM", "SAMBAL", "MAESTRO", "INDOFOOD B/R", "INDOFOOD SMB"], "Bumbu & Rempah"),

(["BAYAM", "KANGKUNG", "CAISIM", "SAWI", "WORTEL", "TOMAT", "TERONG", "BANGKUANG", "JAGUNG MANIS"], "Sayuran"),

(["MANGGA", "NANAS", "ANGGUR", "JAMBU", "LEMON IMPORT", "PEAR"], "Buah"),

(["DAGING", "BAKSO", "KNZLR", "TEMPE"], "Daging & Olahan"),

(["IKAN", "CUMI", "UDANG" ], "Ikan & Seafood"),

(["NUGGET", "HATO", "BELFOODS", "NUG", "SS"], "Frozen Food"),

(["INDOMILK", "FRISIAN", "CIMORY", "OVALTINE", "OATSIDE"], "Susu & Olahan Susu"),

(["INDOMIE", "POP MIE", "MI GEMEZ", "SEDAAP MIE", "SDP MI", "SOTO MI", "IDM M/GORENG"], "Mie Instan"),

(["BISKUAT", "ROMA", "TANGO", "MONDE", "A.T.B MARIE", "CHIKI", "KUSUKA", "KRAKER", "LRSST PILUS", "TOS TOS", "CRUNCHY", "SUKYNCK", "CHOKI CHOKI", "LOTTE", "SERENA", "GERY", "MR.POTATO", "NABATI", "S/Q CHOCO", "SQ BT", "SQ CHK", "SQ CK", "SQ CSW", "CAMPINA"], "Snack"),

(["SUPER BUBUR", "ENERGEN", "NUTRIJEL", "NUTRIJELL", "SUNBBR"], "Makanan Instan"),

(["MR. BREAD", "MY/R ROTI", "ROTI"], "Roti"),

(["AQUA", "AQU", "TEH", "SARIWANGI", "SOSRO", "ULTRA TEH", "KOPI", "NESCAFE", "TOP/COFF", "TIC KPI", "YOU C", "AMUNIZER", "NIPIS MADU", "MARJAN", "C/PANDA", "FOREST GRP", "LEMNRL", "FITMEUP", "G/D INVNL", "LATT", "CASAB", "COL FANT"], "Minuman"),

(["SUNLIGHT", "SNLIGHT", "G/GEN DET", "DETERJEN", "HIT XPRES", "HIT", "TISSU", "TISSUE", "FACIAL TISSUE", "NICE SOFT", "IDM FAC"], "Kebersihan Rumah"),

(["KANTONG PLASTIK", "IDM KTG PLSTK", "REUSABLE", "TAS IDUL", "ALFA ECO", "IDM FIT"], "Kantong & Tas"),

(["SHAMPOO", "SHP", "PANTENE", "H&S", "SABUN", "LUX BW", "BIORE", "NUVO", "CUSSONS", "DEO", "REXONA", "RXONA", "POSH DEO", "NIVEA DEO", "PEPSODENT", "MARINA EDT", "POND", "F/C ROOL", "HERBORIST", "S/PELL BABY", "SOFTENER", "MAMY", "CHARM", "SELECT BLT"], "Perawatan Tubuh"),
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
