"""
extract_text.py — Extract text from a PDF using pdfplumber.

Extracts text page by page. Pages with very low character density (image-heavy)
are flagged in the output but still included — ocr_pdf.py handles those separately.

Usage:
    python3 src/extract_text.py --pdf /path/to/file.pdf --out /tmp/deal_raw.txt

Output:
    Plain text file written to --out.
    JSON metadata written to --out.meta.json:
        { page_count, total_chars, avg_chars_per_page, low_density_pages: [int] }

Exits 1 if file not found or not a PDF.
"""

import argparse
import json
import os
import sys

import pdfplumber


# Pages with fewer than this many characters are flagged as low-density
LOW_DENSITY_THRESHOLD = 150


def extract_text(pdf_path: str, out_path: str) -> dict:
    if not os.path.isfile(pdf_path):
        print(f"ERROR: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        print(f"ERROR: not a PDF file: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    pages_text = []
    low_density_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            text = text.strip()
            pages_text.append(text)
            if len(text) < LOW_DENSITY_THRESHOLD:
                low_density_pages.append(i + 1)  # 1-indexed

    full_text = "\n\n--- PAGE BREAK ---\n\n".join(
        f"[Page {i+1}]\n{t}" for i, t in enumerate(pages_text)
    )

    total_chars = sum(len(t) for t in pages_text)
    avg_chars = total_chars / page_count if page_count > 0 else 0

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    meta = {
        "page_count": page_count,
        "total_chars": total_chars,
        "avg_chars_per_page": round(avg_chars, 1),
        "low_density_pages": low_density_pages,
        "low_density_count": len(low_density_pages),
    }

    meta_path = out_path + ".meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return meta


def main():
    parser = argparse.ArgumentParser(description="Extract text from a PDF.")
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--out", required=True, help="Output path for raw text")
    args = parser.parse_args()

    meta = extract_text(args.pdf, args.out)

    print(f"  Extracted {meta['total_chars']} chars from {meta['page_count']} pages", file=sys.stderr)
    if meta["low_density_pages"]:
        print(
            f"  Low-density pages (image content likely): {meta['low_density_pages']}",
            file=sys.stderr,
        )
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
