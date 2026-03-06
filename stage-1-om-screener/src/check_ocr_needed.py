"""
check_ocr_needed.py — Decide whether a PDF needs OCR based on text density.

Reads the .meta.json written by extract_text.py and applies a threshold:
  - If avg chars per page < threshold → needs full OCR
  - If low_density_pages exist → needs targeted page OCR

Usage:
    python3 src/check_ocr_needed.py --meta /tmp/deal_raw.txt.meta.json

Output (stdout, JSON):
    {
        "needs_ocr": bool,
        "mode": "full" | "targeted" | "none",
        "target_pages": [int],   # page numbers to OCR (1-indexed), empty if full/none
        "reason": str
    }
"""

import argparse
import json
import sys


# If avg chars/page is below this, the whole doc is likely scanned → full OCR
FULL_OCR_THRESHOLD = 100

# Pages below this char count get targeted OCR even in an otherwise text-rich doc
PAGE_OCR_THRESHOLD = 150


def check_ocr_needed(meta: dict) -> dict:
    avg = meta.get("avg_chars_per_page", 0)
    page_count = meta.get("page_count", 0)
    low_density_pages = meta.get("low_density_pages", [])

    # Whole document is essentially image-only
    if avg < FULL_OCR_THRESHOLD:
        return {
            "needs_ocr": True,
            "mode": "full",
            "target_pages": [],
            "reason": f"avg {avg:.0f} chars/page below full-OCR threshold ({FULL_OCR_THRESHOLD})",
        }

    # Mostly text doc but some pages are image-only (embedded spreadsheets, etc.)
    if low_density_pages:
        return {
            "needs_ocr": True,
            "mode": "targeted",
            "target_pages": low_density_pages,
            "reason": (
                f"{len(low_density_pages)} of {page_count} pages have <{PAGE_OCR_THRESHOLD} chars "
                f"(likely embedded images): pages {low_density_pages}"
            ),
        }

    return {
        "needs_ocr": False,
        "mode": "none",
        "target_pages": [],
        "reason": f"avg {avg:.0f} chars/page — text extraction sufficient",
    }


def main():
    parser = argparse.ArgumentParser(description="Check if PDF OCR is needed.")
    parser.add_argument("--meta", required=True, help="Path to .meta.json from extract_text.py")
    args = parser.parse_args()

    try:
        with open(args.meta) as f:
            meta = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: meta file not found: {args.meta}", file=sys.stderr)
        sys.exit(1)

    result = check_ocr_needed(meta)
    print(json.dumps(result, indent=2))

    if result["needs_ocr"]:
        print(f"  OCR needed ({result['mode']}): {result['reason']}", file=sys.stderr)
    else:
        print(f"  No OCR needed: {result['reason']}", file=sys.stderr)


if __name__ == "__main__":
    main()
