"""
discover_inputs.py — Scan a deal folder for supported input files.

Usage:
    python3 src/discover_inputs.py --folder /path/to/deal/folder

Output (stdout, JSON):
    {
        "has_pdf": bool,
        "pdf_path": str | null,
        "has_excel": bool,
        "excel_paths": [str, ...]
    }

Exits 1 with error message if folder is empty or contains no supported files.
"""

import argparse
import json
import os
import sys


SUPPORTED_PDF_EXTS = {".pdf"}
SUPPORTED_EXCEL_EXTS = {".xlsx", ".xls"}


def discover_inputs(folder: str) -> dict:
    if not os.path.isdir(folder):
        print(f"ERROR: folder not found: {folder}", file=sys.stderr)
        sys.exit(1)

    all_files = os.listdir(folder)
    pdf_files = []
    excel_files = []

    for fname in sorted(all_files):
        # Skip hidden files like .gitkeep
        if fname.startswith("."):
            continue
        ext = os.path.splitext(fname)[1].lower()
        full_path = os.path.join(folder, fname)
        if ext in SUPPORTED_PDF_EXTS:
            pdf_files.append(full_path)
        elif ext in SUPPORTED_EXCEL_EXTS:
            excel_files.append(full_path)

    if not pdf_files and not excel_files:
        print(
            f"ERROR: no supported files found in {folder}. "
            "Supported types: .pdf, .xlsx, .xls",
            file=sys.stderr,
        )
        sys.exit(1)

    # If multiple PDFs found, use the largest one (most likely the OM itself)
    pdf_path = None
    if pdf_files:
        pdf_path = max(pdf_files, key=os.path.getsize)
        if len(pdf_files) > 1:
            print(
                f"WARNING: multiple PDFs found, using largest: {os.path.basename(pdf_path)}",
                file=sys.stderr,
            )

    return {
        "has_pdf": bool(pdf_files),
        "pdf_path": pdf_path,
        "has_excel": bool(excel_files),
        "excel_paths": excel_files,
    }


def main():
    parser = argparse.ArgumentParser(description="Discover deal input files in a folder.")
    parser.add_argument("--folder", required=True, help="Path to deal folder")
    args = parser.parse_args()

    result = discover_inputs(args.folder)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
