"""Ekstrak produk dari PDF struk Super Indo ke Excel."""

import sys
import re
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

try:
    import pdfplumber
except ImportError:
    sys.exit("ERROR: pdfplumber belum terinstall. Jalankan: pip install pdfplumber")

try:
    import pandas as pd
except ImportError:
    sys.exit("ERROR: pandas/openpyxl belum terinstall. Jalankan: pip install pandas openpyxl")


PRODUCT_LINE = re.compile(
    r"^(.+?)\s+(\d{1,4})\s+\d{1,3}\.\d{3}\s+\d{1,3}\.\d{3}$"
)

SKIP_PATTERNS = [
    r"^PT LION", r"^NPWP", r"^Tanggal", r"^JL\.", r"^KEL\.", r"^KEC\.",
    r"^Telp", r"^\d{2}-\d{2}-\d{2}",
    r"^DESKRIPSI", r"^={3,}", r"^-{3,}",
    r"^HEMAT", r"^Sub Total", r"^Pembayaran", r"^Nomor",
    r"^Hemat", r"^Total", r"^BTKP", r"^BKP", r"^DPP",
    r"^Member", r"^\*\*", r"^SARAN", r"^TELP", r"^WHATSAPP",
    r"^SENIN", r"^email", r"^www",
]

PRODUK_GRAM = {
    "TELUR AYAM NEGERI",
    "JAGUNG MANIS KUPA",
}

OUTPUT_EXCEL = "hasil_barang_receipt.xlsx"


def is_skip(line: str) -> bool:
    return any(re.match(pat, line) for pat in SKIP_PATTERNS)


def extract_total_item(text: str):
    m = re.search(r"Total Item\s*:\s*(\d+)", text)
    return int(m.group(1)) if m else None


def normalize_date(day: str, month: str, year: str) -> str:
    year_int = int(year)
    if year_int < 100:
        year_int += 2000 if year_int < 70 else 1900
    return f"{year_int:04d}-{int(month):02d}-{int(day):02d}"


def extract_transaction_date(text: str) -> str:
    for line in text.splitlines():
        if "Tanggal Pengukuhan" in line:
            continue
        match = re.search(r"\b(\d{2})[-/](\d{2})[-/](\d{2,4}),?\s*\(\d{2}:\d{2}:\d{2}\)", line)
        if match:
            return normalize_date(match.group(1), match.group(2), match.group(3))
    return ""


def parse_receipt(pdf_path: str) -> dict:
    path = Path(pdf_path)
    result = {
        "path": str(path),
        "filename": path.name,
        "tanggal_transaksi": "",
        "products": [],
        "total_item_struk": None,
        "raw_rows": 0,
        "valid": False,
        "notes": [],
    }

    if not path.exists():
        result["notes"].append("File tidak ditemukan")
        return result

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        result["notes"].append(f"Gagal buka PDF: {e}")
        return result

    result["tanggal_transaksi"] = extract_transaction_date(full_text)

    raw_products = []
    for line in full_text.splitlines():
        line = line.strip()
        if not line or is_skip(line):
            continue
        m = PRODUCT_LINE.match(line)
        if m:
            raw_products.append((m.group(1).strip(), int(m.group(2))))

    result["raw_rows"] = len(raw_products)

    merged: dict[str, int] = defaultdict(int)
    for nama, qty in raw_products:
        merged[nama] += qty

    for nama, qty in merged.items():
        satuan = "gram" if any(k in nama for k in PRODUK_GRAM) else "pcs"
        result["products"].append((nama, qty, satuan))

    total_item_struk = extract_total_item(full_text)
    result["total_item_struk"] = total_item_struk

    unique_count = len(result["products"])
    if total_item_struk is not None:
        if unique_count == total_item_struk or len(raw_products) == total_item_struk:
            result["valid"] = True
            if len(raw_products) != unique_count and unique_count == total_item_struk:
                result["notes"].append(
                    f"Ada duplikat nama ({len(raw_products)} baris -> {unique_count} unique), sudah di-merge."
                )
        else:
            result["notes"].append(
                f"Mismatch: parsed {unique_count} unique / {len(raw_products)} raw, struk: {total_item_struk}"
            )
    else:
        result["notes"].append("'Total Item' tidak ditemukan di struk - skip validasi.")

    return result


def print_result(result: dict, index: int, total: int):
    fname = result["filename"]
    products = result["products"]

    print()
    print(f"[{index}/{total}] {fname}")

    if not products:
        print("  Tidak ada produk ter-parse.")
        for note in result["notes"]:
            print(f"  Catatan: {note}")
        print("-" * 54)
        return

    print(f"  {'No':<4} {'Nama Produk':<30} {'Qty':>6}  Satuan")
    print(f"  {'-'*48}")
    for i, (nama, qty, satuan) in enumerate(products, 1):
        print(f"  {i:<4} {nama:<30} {qty:>6}  {satuan}")
    print(f"  {'-'*48}")
    print(f"  Jenis produk : {len(products)}  |  Raw rows : {result['raw_rows']}", end="")
    if result["total_item_struk"] is not None:
        status = "VALID" if result["valid"] else "MISMATCH"
        print(f"  |  Total Item struk : {result['total_item_struk']}  {status}")
    else:
        print()
    for note in result["notes"]:
        print(f"  Catatan: {note}")
    print("-" * 54)


def clean_product_name(name: str) -> str:
    name = re.sub(r"\d+(?:[.,]\d+)?\s*(?:GR|G|KG|ML|L|PCS)?", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+", " ", name)
    return name.strip(" -_/")


def build_excel_rows(results: list[dict]) -> list[dict]:
    rows = []
    for struk_ke, result in enumerate(results, 1):
        for nama, _qty, _satuan in result["products"]:
            clean_name = clean_product_name(nama)
            if clean_name:
                rows.append(
                    {
                        "struk_ke": struk_ke,
                        "tanggal_transaksi": result["tanggal_transaksi"],
                        "nama_barang": clean_name,
                    }
                )
    return rows


def export_to_excel(results: list[dict], output_path: Path) -> None:
    rows = build_excel_rows(results)
    if not rows:
        print("\nTidak ada data barang untuk diekspor ke Excel.")
        return

    df = pd.DataFrame(rows)

    try:
        writer = pd.ExcelWriter(output_path, engine="openpyxl")
    except PermissionError:
        output_path = output_path.with_name(
            f"{output_path.stem}_{datetime.now():%Y%m%d_%H%M%S}{output_path.suffix}"
        )
        writer = pd.ExcelWriter(output_path, engine="openpyxl")

    with writer:
        df.to_excel(writer, index=False, sheet_name="nama_barang")

        worksheet = writer.sheets["nama_barang"]
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            column_letter = column_cells[0].column_letter
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)

    print(f"\nExcel berhasil dibuat: {output_path}")


def resolve_pdf_files(args: list[str]) -> list[str]:
    if not args:
        return collect_from_folder(Path.cwd())

    if len(args) == 1 and Path(args[0]).is_dir():
        return collect_from_folder(args[0])

    return [a for a in args if a.lower().endswith(".pdf")]


def collect_from_folder(folder_path: str) -> list[str]:
    folder = Path(folder_path)
    if not folder.is_dir():
        sys.exit(f"ERROR: Bukan folder valid: {folder_path}")
    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"ERROR: Tidak ada file PDF di folder: {folder_path}")
    print(f"Ditemukan {len(pdfs)} file PDF di '{folder}'")
    return [str(p) for p in pdfs]


def main():
    pdf_files = resolve_pdf_files(sys.argv[1:])

    if not pdf_files:
        sys.exit("ERROR: Tidak ada file PDF yang bisa diproses.")

    total = len(pdf_files)
    print(f"\nMemproses {total} file receipt Super Indo...\n")
    print("=" * 54)

    summary = {"total": total, "valid": 0, "invalid": 0, "error": 0}
    invalid_files = []
    results = []

    for i, pdf_path in enumerate(pdf_files, 1):
        result = parse_receipt(pdf_path)
        results.append(result)
        print_result(result, i, total)

        if not result["products"]:
            summary["error"] += 1
            invalid_files.append((result["filename"], "Gagal parse"))
        elif result["valid"]:
            summary["valid"] += 1
        else:
            summary["invalid"] += 1
            invalid_files.append((result["filename"], result["notes"][0] if result["notes"] else "Mismatch"))

    print()
    print("=" * 54)
    print(f"  SUMMARY - {total} file diproses")
    print(f"  Valid        : {summary['valid']}")
    print(f"  Mismatch     : {summary['invalid']}")
    print(f"  Error/Kosong : {summary['error']}")
    if invalid_files:
        print(f"\n  File yang perlu dicek manual:")
        for fname, reason in invalid_files:
            print(f"    - {fname}: {reason}")
    print("=" * 54)

    export_to_excel(results, Path.cwd() / OUTPUT_EXCEL)


if __name__ == "__main__":
    main()
