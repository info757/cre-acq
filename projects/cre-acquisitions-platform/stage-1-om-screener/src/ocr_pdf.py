"""
ocr_pdf.py — OCR a PDF and merge results into the existing text file.

Supports two modes (from check_ocr_needed.py output):
  - full:     OCR every page, replace the entire text file
  - targeted: OCR only specified pages, splice results into existing text file

Uses pdf2image to render pages → Tesseract for OCR.

Usage:
    python3 src/ocr_pdf.py --pdf /path/to/file.pdf \
                           --txt /tmp/deal_raw.txt \
                           --mode targeted \
                           --pages '[4,9,10]'

    python3 src/ocr_pdf.py --pdf /path/to/file.pdf \
                           --txt /tmp/deal_raw.txt \
                           --mode full

Output:
    Updates --txt in place. Overwrites low-density page sections with OCR text.
    Exits 1 on failure.
"""

import argparse
import json
import os
import re
import sys
import tempfile

from pdf2image import convert_from_path
import pytesseract


def ocr_pages(pdf_path: str, page_numbers: list[int]) -> dict[int, str]:
    """
    OCR specific pages (1-indexed) from a PDF.
    Returns dict: { page_number: ocr_text }
    """
    results = {}

    # Convert only the needed pages (pdf2image uses 1-indexed first_page/last_page)
    # For targeted, we convert each page range individually to avoid loading the whole doc
    all_needed = sorted(page_numbers)

    with tempfile.TemporaryDirectory() as tmpdir:
        for page_num in all_needed:
            images = convert_from_path(
                pdf_path,
                first_page=page_num,
                last_page=page_num,
                dpi=300,
                output_folder=tmpdir,
                fmt="png",
            )
            if not images:
                print(f"  WARNING: could not render page {page_num}", file=sys.stderr)
                results[page_num] = ""
                continue

            text = pytesseract.image_to_string(images[0], config="--psm 6")
            results[page_num] = text.strip()
            print(f"  OCR page {page_num}: {len(text.strip())} chars extracted", file=sys.stderr)

    return results


def splice_ocr_into_text(existing_text: str, ocr_results: dict[int, str]) -> str:
    """
    Replace [Page N] sections in the existing text with OCR output.
    Leaves all other pages untouched.
    """
    lines = existing_text.split("\n")
    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect [Page N] header
        match = re.match(r"^\[Page (\d+)\]$", line.strip())
        if match:
            page_num = int(match.group(1))
            if page_num in ocr_results:
                # Replace this page section with OCR text
                output_lines.append(f"[Page {page_num}] [OCR]")
                output_lines.append(ocr_results[page_num])
                i += 1
                # Skip the original (low-density) page content until next page break or end
                while i < len(lines):
                    if lines[i].strip().startswith("--- PAGE BREAK ---") or re.match(r"^\[Page \d+\]$", lines[i].strip()):
                        break
                    i += 1
                continue

        output_lines.append(line)
        i += 1

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="OCR a PDF and update the text file.")
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--txt", required=True, help="Path to existing text file (updated in place)")
    parser.add_argument("--mode", required=True, choices=["full", "targeted"], help="OCR mode")
    parser.add_argument("--pages", default="[]", help="JSON array of page numbers for targeted mode")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "targeted":
        try:
            page_numbers = json.loads(args.pages)
        except json.JSONDecodeError:
            print("ERROR: --pages must be a valid JSON array", file=sys.stderr)
            sys.exit(1)

        if not page_numbers:
            print("ERROR: targeted mode requires --pages with at least one page number", file=sys.stderr)
            sys.exit(1)

        print(f"  Targeted OCR: pages {page_numbers}", file=sys.stderr)
        ocr_results = ocr_pages(args.pdf, page_numbers)

        # Splice into existing text
        if os.path.isfile(args.txt):
            with open(args.txt, encoding="utf-8") as f:
                existing = f.read()
        else:
            existing = ""

        updated = splice_ocr_into_text(existing, ocr_results)
        with open(args.txt, "w", encoding="utf-8") as f:
            f.write(updated)

        print(f"  Spliced OCR into {args.txt}", file=sys.stderr)

    elif args.mode == "full":
        import pdfplumber

        with pdfplumber.open(args.pdf) as pdf:
            total_pages = len(pdf.pages)

        print(f"  Full OCR: {total_pages} pages", file=sys.stderr)
        all_pages = list(range(1, total_pages + 1))
        ocr_results = ocr_pages(args.pdf, all_pages)

        # Build fresh text file
        sections = []
        for page_num in all_pages:
            text = ocr_results.get(page_num, "")
            sections.append(f"[Page {page_num}] [OCR]\n{text}")

        full_text = "\n\n--- PAGE BREAK ---\n\n".join(sections)
        os.makedirs(os.path.dirname(args.txt) if os.path.dirname(args.txt) else ".", exist_ok=True)
        with open(args.txt, "w", encoding="utf-8") as f:
            f.write(full_text)

        print(f"  Full OCR written to {args.txt}", file=sys.stderr)

    print("  OCR complete", file=sys.stderr)


if __name__ == "__main__":
    main()
