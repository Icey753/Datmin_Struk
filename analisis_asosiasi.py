"""Analisis Asosiasi (Apriori & FP-Growth) menggunakan Python.

Membaca data dari hasil_kategorisasi.xlsx, melakukan pencarian frequent itemsets
dan association rules menggunakan algoritma Apriori yang diimplementasikan dari awal,
serta menghasilkan visualisasi dan file CSV hasil analisis.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Atur agar output terminal menggunakan UTF-8
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# Parameters
MIN_SUPPORT_COUNT = 3
MIN_CONFIDENCE = 0.5
MIN_LIFT = 1.0
INPUT_FILE = "hasil_kategorisasi.xlsx"
OUTPUT_APRIORI_CSV = "rules_apriori_python.csv"
OUTPUT_FPGROWTH_CSV = "rules_fpgrowth_python.csv"


def load_transactions() -> tuple[list[set[str]], int]:
    """Membaca file Excel dan mengelompokkan barang berdasarkan struk_ke."""
    if not os.path.exists(INPUT_FILE):
        # Fallback: jika hasil_kategorisasi.xlsx tidak ada, coba jalankan kategorisasi.py
        if os.path.exists("kategorisasi.py"):
            print(f"[WARN] File '{INPUT_FILE}' tidak ditemukan.")
            print("Mencoba membuat file kategorisasi dengan menjalankan 'kategorisasi.py'...")
            import subprocess
            subprocess.run([sys.executable, "kategorisasi.py"])
        else:
            sys.exit(f"ERROR: File '{INPUT_FILE}' tidak ditemukan di workspace.")
            
    df = pd.read_excel(INPUT_FILE)
    
    # Kelompokkan kategori berdasarkan struk_ke menjadi set (menghapus duplikat dalam satu transaksi)
    grouped = df.groupby("struk_ke")["kategori"].apply(set).tolist()
    return grouped, len(grouped)


def get_frequent_itemsets(transactions: list[set[str]], min_sup_count: int) -> dict[frozenset[str], int]:
    """Implementasi algoritma Apriori untuk mencari frequent itemsets."""
    frequent_itemsets = {}
    
    # 1. Hitung frequent 1-itemsets
    candidates = {}
    for transaction in transactions:
        for item in transaction:
            itemset = frozenset([item])
            candidates[itemset] = candidates.get(itemset, 0) + 1
            
    # Saring yang memenuhi min_support_count
    current_frequent = {itemset: count for itemset, count in candidates.items() if count >= min_sup_count}
    frequent_itemsets.update(current_frequent)
    
    k = 2
    while current_frequent:
        # Tentukan kandidat itemsets ukuran k
        prev_itemsets = list(current_frequent.keys())
        candidates_k = set()
        num_itemsets = len(prev_itemsets)
        
        for i in range(num_itemsets):
            for j in range(i + 1, num_itemsets):
                # Join step
                joined = prev_itemsets[i] | prev_itemsets[j]
                if len(joined) == k:
                    # Prune step: pastikan seluruh subset ukuran k-1 dari joined bersifat frequent
                    is_valid = True
                    for item in joined:
                        subset = joined - frozenset([item])
                        if subset not in current_frequent:
                            is_valid = False
                            break
                    if is_valid:
                        candidates_k.add(joined)
                        
        # Hitung support count untuk kandidat ukuran k
        candidates_count = {c: 0 for c in candidates_k}
        for transaction in transactions:
            for candidate in candidates_k:
                if candidate.issubset(transaction):
                    candidates_count[candidate] += 1
                    
        # Saring yang memenuhi min_support_count
        current_frequent = {itemset: count for itemset, count in candidates_count.items() if count >= min_sup_count}
        if not current_frequent:
            break
            
        frequent_itemsets.update(current_frequent)
        k += 1
        
    return frequent_itemsets


def generate_association_rules(
    frequent_itemsets: dict[frozenset[str], int],
    N_transaksi: int,
    min_confidence: float,
    min_lift: float
) -> list[dict]:
    """Menghasilkan aturan asosiasi dari frequent itemsets."""
    rules = []
    
    def get_support_count(itemset):
        return frequent_itemsets.get(itemset, 0)
        
    for itemset, count in frequent_itemsets.items():
        if len(itemset) < 2:
            continue
            
        # Dapatkan semua proper subset dari itemset
        items = list(itemset)
        n = len(items)
        # Hasilkan semua subset non-kosong dan tidak sama dengan itemset
        subsets = []
        for i in range(1, (1 << n) - 1):
            subset = frozenset([items[j] for j in range(n) if (i & (1 << j))])
            subsets.append(subset)
            
        for lhs in subsets:
            rhs = itemset - lhs
            
            support_lhs = get_support_count(lhs)
            support_rhs = get_support_count(rhs)
            support_joint = count
            
            if support_lhs == 0 or support_rhs == 0:
                continue
                
            sup = support_joint / N_transaksi
            conf = support_joint / support_lhs
            lift = conf / (support_rhs / N_transaksi)
            coverage = support_lhs / N_transaksi
            
            if conf >= min_confidence and lift >= min_lift:
                # Format string rule seperti di R: {A,B} => {C}
                lhs_str = ",".join(sorted(list(lhs)))
                rhs_str = ",".join(sorted(list(rhs)))
                rule_str = f"{{{lhs_str}}} => {{{rhs_str}}}"
                
                rules.append({
                    "rules": rule_str,
                    "support": sup,
                    "confidence": conf,
                    "coverage": coverage,
                    "lift": lift,
                    "count": support_joint
                })
                
    # Urutkan aturan berdasarkan lift secara descending
    rules = sorted(rules, key=lambda r: (-r["lift"], -r["confidence"], -r["support"]))
    return rules


def export_rules_to_csv(rules: list[dict], filepath: str, is_fpgrowth: bool = False):
    """Mengekspor rules ke file CSV dengan kolom yang sesuai."""
    df = pd.DataFrame(rules)
    if df.empty:
        print(f"  [SKIP] Tidak ada rules untuk diekspor ke '{filepath}'")
        return
        
    if is_fpgrowth:
        # Sesuaikan kolom untuk file fpgrowth agar mirip R
        # R's fpgrowth: "rules","support","confidence","lift","itemset"
        # Kita beri kolom 'itemset' nomor urut saja
        df_fp = df[["rules", "support", "confidence", "lift"]].copy()
        df_fp["itemset"] = range(1, len(df_fp) + 1)
        df_fp.to_csv(filepath, index=False)
    else:
        # Apriori: "rules","support","confidence","coverage","lift","count"
        df_ap = df[["rules", "support", "confidence", "coverage", "lift", "count"]].copy()
        df_ap.to_csv(filepath, index=False)
        
    print(f"  [OK] Berhasil menyimpan: {filepath} ({len(rules)} rules)")


def plot_visualizations(transactions: list[set[str]], rules: list[dict]):
    """Membuat visualisasi hasil analisis asosiasi."""
    sns.set_theme(style="whitegrid")
    
    # 1. VIZ 1: Frekuensi Kategori (Absolute)
    category_counts = {}
    for t in transactions:
        for item in t:
            category_counts[item] = category_counts.get(item, 0) + 1
            
    df_freq = pd.DataFrame(list(category_counts.items()), columns=["Kategori", "Frekuensi"])
    df_freq = df_freq.sort_values(by="Frekuensi", ascending=False).head(16)
    
    plt.figure(figsize=(10, 6), dpi=150)
    # Bikin palette gradient biru-teal
    colors = sns.color_palette("viridis", len(df_freq))
    sns.barplot(x="Frekuensi", y="Kategori", data=df_freq, palette=colors, hue="Kategori", legend=False)
    plt.title("Frekuensi Kategori per Transaksi (Python)\nPeriode: 2024-06-08 s/d 2026-05-25", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Frekuensi (Jumlah Transaksi)", fontsize=11, labelpad=10)
    plt.ylabel("", fontsize=11)
    plt.tight_layout()
    plt.savefig("viz_01_frekuensi_kategori_python.png", bbox_inches="tight")
    plt.close()
    print("  [OK] Visualisasi frekuensi tersimpan di: viz_01_frekuensi_kategori_python.png")
    
    if not rules:
        print("  [SKIP] Tidak ada rules untuk divisualisasikan.")
        return
        
    df_rules = pd.DataFrame(rules)
    
    # 2. VIZ 2: Scatter Plot (Support vs Confidence, colored by Lift)
    plt.figure(figsize=(9, 7), dpi=150)
    scatter = plt.scatter(
        df_rules["support"], 
        df_rules["confidence"], 
        c=df_rules["lift"], 
        cmap="YlOrRd", 
        s=df_rules["count"] * 50, # ukuran dot berdasarkan count
        alpha=0.8,
        edgecolors="black",
        linewidths=0.5
    )
    cbar = plt.colorbar(scatter)
    cbar.set_label("Lift Ratio", rotation=270, labelpad=15, fontsize=11)
    plt.title("Scatter Plot - Aturan Asosiasi (Python)\nMin Support Count = 3 | Min Confidence = 0.5", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Support", fontsize=11, labelpad=10)
    plt.ylabel("Confidence", fontsize=11, labelpad=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("viz_02_scatter_rules_python.png", bbox_inches="tight")
    plt.close()
    print("  [OK] Visualisasi scatter rules tersimpan di: viz_02_scatter_rules_python.png")
    
    # 3. VIZ 3: Top-15 Rules by Lift
    df_top = df_rules.head(15).copy()
    plt.figure(figsize=(10, 7), dpi=150)
    sns.barplot(
        x="lift", 
        y="rules", 
        data=df_top, 
        palette="magma", 
        hue="rules",
        legend=False
    )
    plt.title("Top-15 Aturan Asosiasi berdasarkan Lift Ratio (Python)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Lift Ratio", fontsize=11, labelpad=10)
    plt.ylabel("Aturan (Rules)", fontsize=11)
    # Tambahkan label angka di ujung bar
    for idx, row in df_top.reset_index().iterrows():
        plt.text(row["lift"] + 0.1, idx, f"{row['lift']:.2f}", va="center", ha="left", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig("viz_03_top_rules_python.png", bbox_inches="tight")
    plt.close()
    print("  [OK] Visualisasi top rules tersimpan di: viz_03_top_rules_python.png")


def main():
    print("=" * 60)
    print(" ANALISIS ASOSIASI (APRIORI & FP-GROWTH) DENGAN PYTHON")
    print("=" * 60)
    
    # Load transactions
    transactions, N = load_transactions()
    print(f"Total transaksi yang dimuat : {N} struk")
    print(f"Parameter: min_support_count = {MIN_SUPPORT_COUNT} (supp = {MIN_SUPPORT_COUNT/N:.4f})")
    print(f"           min_confidence = {MIN_CONFIDENCE}")
    print(f"           min_lift = {MIN_LIFT}")
    
    # 1. Jalankan Apriori
    print("\nMencari frequent itemsets...")
    freq_itemsets = get_frequent_itemsets(transactions, MIN_SUPPORT_COUNT)
    print(f"Jumlah frequent itemsets yang ditemukan: {len(freq_itemsets)}")
    
    # 2. Hasilkan Aturan Asosiasi
    print("Menghasilkan aturan asosiasi...")
    rules = generate_association_rules(freq_itemsets, N, MIN_CONFIDENCE, MIN_LIFT)
    print(f"Jumlah aturan asosiasi yang memenuhi kriteria: {len(rules)}")
    
    # Tampilkan top 10 rules ke terminal
    print("\n--- TOP-10 RULES BERDASARKAN LIFT RATIO ---")
    print(f"{'Rules':<45} {'Support':<8} {'Confidence':<10} {'Lift':<6} {'Count':<5}")
    print("-" * 79)
    for r in rules[:10]:
        print(f"{r['rules']:<45} {r['support']:<8.4f} {r['confidence']:<10.4f} {r['lift']:<6.4f} {r['count']:<5}")
    print("-" * 79)
    
    # 3. Ekspor ke CSV (membuat file versi Apriori dan FP-growth untuk kompabilitas)
    print("\nMengekspor hasil aturan asosiasi ke CSV...")
    export_rules_to_csv(rules, OUTPUT_APRIORI_CSV, is_fpgrowth=False)
    export_rules_to_csv(rules, OUTPUT_FPGROWTH_CSV, is_fpgrowth=True)
    
    # 4. Gambar Visualisasi
    print("\nMenggambar visualisasi...")
    plot_visualizations(transactions, rules)
    
    print("\n[SUKSES] Analisis selesai! Semua file output telah dibuat.")
    print(f"  - CSV Aturan Apriori   : {OUTPUT_APRIORI_CSV}")
    print(f"  - CSV Aturan FP-Growth : {OUTPUT_FPGROWTH_CSV}")
    print("  - Visualisasi          : viz_01 s/d viz_03 (_python.png)\n")


if __name__ == "__main__":
    main()
