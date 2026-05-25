"""Ekstrak produk dari gambar struk Alfamart ke Excel."""

import base64
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

try:
    import pandas as pd
except ImportError:
    sys.exit("ERROR: pandas/openpyxl belum terinstall. Jalankan: pip install pandas openpyxl")


DEFAULT_IMAGE_FOLDER = "alfamaret"
OUTPUT_EXCEL = "hasil_barang_alfamaret.xlsx"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

STOP_PATTERNS = [
    r"^anda mendapatkan",
    r"^stamp",
    r"^total item",
    r"^qris",
    r"^kembalian",
    r"^dpp",
    r"^ppn",
    r"^tgl",
    r"^tgi",
    r"^member",
    r"^a-poin",
    r"^struk anda",
    r"^alfagift",
    r"^potensi",
    r"^sms/wa",
    r"^kritik",
]

HEADER_PATTERNS = [
    r"^alfamart",
    r"^alfa tower",
    r"^npwp",
    r"^jl\.",
    r"^kasir",
]


def powershell_ocr_script() -> str:
    return r"""
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Path = $env:OCR_IMAGE_PATH

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq "AsTask" -and
    $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]

function Await($AsyncOp, [Type]$ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $task = $asTask.Invoke($null, @($AsyncOp))
    $task.Wait() | Out-Null
    return $task.Result
}

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($Path)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()

if ($null -eq $engine) {
    throw "Windows OCR engine tidak tersedia di komputer ini."
}

$result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
$lines = @($result.Lines | ForEach-Object { $_.Text })
$lines | ConvertTo-Json -Compress
"""


def ocr_image(image_path: Path) -> list[str]:
    script = powershell_ocr_script()
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    env = {**dict(os_environ()), "OCR_IMAGE_PATH": str(image_path.resolve())}

    completed = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())

    output = completed.stdout.strip()
    if not output:
        return []

    data = json.loads(output)
    if isinstance(data, str):
        return [data]
    return [str(line) for line in data if str(line).strip()]


def os_environ() -> dict[str, str]:
    import os

    return dict(os.environ)


def is_stop_line(line: str) -> bool:
    lower = line.lower().strip()
    return any(re.search(pattern, lower) for pattern in STOP_PATTERNS)


def is_header_line(line: str) -> bool:
    lower = line.lower().strip()
    return any(re.search(pattern, lower) for pattern in HEADER_PATTERNS)


def looks_like_price_or_total(line: str) -> bool:
    clean = line.strip()
    return bool(re.fullmatch(r"[\d\s,.:-]+", clean))


def clean_product_name(name: str) -> str:
    name = re.sub(r"\b\d+\s*[xX]\s*\d+\b", "", name)
    name = re.sub(r"\d+(?:[.,]\d+)?\s*(?:GR|G|KG|ML|L|PCS)?", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+", " ", name)
    return name.strip(" -_/")


def normalize_date(day: str, month: str, year: str) -> str:
    year_int = int(year)
    if year_int < 100:
        year_int += 2000 if year_int < 70 else 1900
    return f"{year_int:04d}-{int(month):02d}-{int(day):02d}"


def extract_transaction_date(lines: list[str]) -> str:
    for line in lines:
        match = re.search(r"\b(\d{2})[-/](\d{2})[-/](\d{2,4})\b", line)
        if match:
            return normalize_date(match.group(1), match.group(2), match.group(3))
    return ""


def parse_products(lines: list[str]) -> list[str]:
    products = []
    in_items = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        lower = line.lower()
        if lower.startswith("bon "):
            in_items = True
            continue

        if not in_items:
            continue

        if is_stop_line(line):
            break

        if is_header_line(line) or looks_like_price_or_total(line):
            continue

        clean_name = clean_product_name(line)
        if clean_name and clean_name.lower().rstrip(".") != "disc":
            products.append(clean_name)

    return products


def resolve_image_files(args: list[str]) -> list[Path]:
    if not args:
        return collect_from_folder(Path.cwd() / DEFAULT_IMAGE_FOLDER)

    if len(args) == 1 and Path(args[0]).is_dir():
        return collect_from_folder(Path(args[0]))

    return [Path(arg) for arg in args if Path(arg).suffix.lower() in IMAGE_EXTENSIONS]


def collect_from_folder(folder_path: Path) -> list[Path]:
    if not folder_path.is_dir():
        sys.exit(f"ERROR: Folder tidak ditemukan: {folder_path}")

    images = sorted(path for path in folder_path.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        sys.exit(f"ERROR: Tidak ada gambar struk di folder: {folder_path}")

    print(f"Ditemukan {len(images)} gambar di '{folder_path}'")
    return images


def export_to_excel(rows: list[dict], output_path: Path) -> Path | None:
    if not rows:
        print("\nTidak ada nama barang untuk diekspor.")
        return None

    df = pd.DataFrame(rows, columns=["struk_ke", "tanggal_transaksi", "nama_barang"])

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

    return output_path


def main() -> None:
    image_files = resolve_image_files(sys.argv[1:])
    rows = []
    failed = []

    print(f"\nMemproses {len(image_files)} struk Alfamart dari gambar...\n")

    for struk_ke, image_path in enumerate(image_files, 1):
        try:
            lines = ocr_image(image_path)
            tanggal_transaksi = extract_transaction_date(lines)
            products = parse_products(lines)
        except Exception as exc:
            tanggal_transaksi = ""
            products = []
            failed.append((image_path.name, str(exc)))

        tanggal_label = tanggal_transaksi or "-"
        print(f"[{struk_ke}/{len(image_files)}] {image_path.name}: {len(products)} barang ({tanggal_label})")
        for product in products:
            print(f"  - {product}")
            rows.append(
                {
                    "struk_ke": struk_ke,
                    "tanggal_transaksi": tanggal_transaksi,
                    "nama_barang": product,
                }
            )

        if not products and image_path.name not in [name for name, _reason in failed]:
            failed.append((image_path.name, "Tidak ada barang terdeteksi"))

    output_path = export_to_excel(rows, Path.cwd() / OUTPUT_EXCEL)

    print("\nSUMMARY")
    print(f"  Struk diproses : {len(image_files)}")
    print(f"  Baris barang   : {len(rows)}")
    print(f"  Gagal/kosong   : {len(failed)}")
    if output_path:
        print(f"  Excel          : {output_path}")

    if failed:
        print("\nFile yang perlu dicek manual:")
        for filename, reason in failed:
            print(f"  - {filename}: {reason}")


if __name__ == "__main__":
    main()
