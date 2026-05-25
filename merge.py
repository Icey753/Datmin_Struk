"""Gabungkan output semua sumber struk ke satu Excel."""

import os
import pandas as pd


FILES = [
    ("hasil_barang_alfamaret.xlsx", "Alfamaret"),
    ("hasil_barang_indomaret.xlsx", "Indomaret"),
    ("hasil_barang_receipt.xlsx",   "SuperIndo"),
]

OUTPUT = "hasil_gabungan.xlsx"


def load_files() -> list[pd.DataFrame]:
    dfs = []
    for filename, sumber in FILES:
        if not os.path.exists(filename):
            print(f"[SKIP] File tidak ditemukan: {filename}")
            continue
        df = pd.read_excel(filename)
        df["sumber"] = sumber
        print(f"[OK]   Dibaca: {filename}  ({len(df)} baris, {df['struk_ke'].nunique()} struk)")
        dfs.append(df)
    return dfs


def merge_and_renumber(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    merged = pd.concat(dfs, ignore_index=True)

    merged["tanggal_transaksi"] = pd.to_datetime(merged["tanggal_transaksi"], errors="coerce").dt.date

    merged = merged.sort_values(
        by=["tanggal_transaksi", "sumber", "struk_ke"],
        ignore_index=True,
    )

    group_keys = merged[["tanggal_transaksi", "sumber", "struk_ke"]].apply(
        lambda r: (r["tanggal_transaksi"], r["sumber"], r["struk_ke"]), axis=1
    )
    unique_groups = {v: i + 1 for i, v in enumerate(dict.fromkeys(group_keys))}
    merged["struk_ke"] = group_keys.map(unique_groups)

    cols = ["struk_ke", "sumber", "tanggal_transaksi", "nama_barang"]
    merged = merged[cols]

    return merged


def export(df: pd.DataFrame, output_path: str) -> None:
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"\nFile berhasil disimpan: {output_path}")
    print(f"   Total baris     : {len(df)}")
    print(f"   Total struk     : {df['struk_ke'].nunique()}")
    print(f"   Rentang tanggal : {df['tanggal_transaksi'].min()} s/d {df['tanggal_transaksi'].max()}")
    print(f"   Sumber          : {', '.join(df['sumber'].unique())}")


def main():
    print("=" * 55)
    print("  MERGE: hasil_barang_alfamaret + indomaret + receipt")
    print("=" * 55)

    dfs = load_files()
    if not dfs:
        print("[ERROR] Tidak ada file yang bisa diproses.")
        return

    merged = merge_and_renumber(dfs)
    export(merged, OUTPUT)


if __name__ == "__main__":
    main()
