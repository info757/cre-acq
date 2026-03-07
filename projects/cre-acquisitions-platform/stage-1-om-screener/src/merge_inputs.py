"""
merge_inputs.py — Merge Excel metrics and Claude-extracted metrics from OM text.

Merge rule: Excel values take priority field-by-field.
            Claude fills any remaining null fields.
            Source tag written per field: "excel" | "claude" | null

Usage:
    python3 src/merge_inputs.py \
        [--raw-text /tmp/deal_raw.txt] \
        [--excel /tmp/deal_excel.json] \
        --prompt prompts/om-extractor.md \
        --out /tmp/deal_extracted.json

At least one of --raw-text or --excel must be provided.

Output: full ExtractedMetrics JSON written to --out, with a _sources dict
        indicating the origin of each field value.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import anthropic
from dotenv import load_dotenv

# Load .env from the project root (stage-1-om-screener/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def call_claude(raw_text: str, prompt_template: str) -> dict:
    """Send OM text to Claude, return parsed JSON metrics."""
    prompt = prompt_template.replace("{{raw_text}}", raw_text)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences if model adds them
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(
            line for line in lines
            if not line.startswith("```")
        )

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[merge_inputs] Claude returned invalid JSON: {e}", file=sys.stderr)
        print(f"[merge_inputs] Raw response: {raw[:500]}", file=sys.stderr)
        sys.exit(1)


def get_nested(d: dict, *keys):
    """Safely get a nested value, returning None if any key is missing."""
    for key in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(key)
    return d


def set_nested(d: dict, keys: list, value):
    """Set a nested value given a list of keys."""
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------

# All scalar field paths in ExtractedMetrics (section, field_name)
SCALAR_FIELDS = [
    ("property", "type"),
    ("property", "market"),
    ("property", "submarket"),
    ("property", "address"),
    ("property", "vintage"),
    ("property", "units"),
    ("property", "total_sf"),
    ("financials", "asking_price"),
    ("financials", "price_per_unit"),
    ("financials", "price_per_sf"),
    ("financials", "noi_trailing"),
    ("financials", "noi_proforma"),
    ("financials", "cap_rate_trailing"),
    ("financials", "cap_rate_proforma"),
    ("financials", "occupancy_current"),
    ("financials", "occupancy_economic"),
    ("financials", "gross_revenue"),
    ("financials", "total_expenses"),
    ("financials", "expense_ratio"),
    ("debt", "ltv"),
    ("debt", "dscr"),
    ("debt", "interest_rate"),
    ("debt", "maturity_date"),
    ("debt", "assumable"),
]

EMPTY_METRICS = {
    "property": {
        "type": None, "market": None, "submarket": None,
        "address": None, "vintage": None, "units": None, "total_sf": None,
    },
    "financials": {
        "asking_price": None, "price_per_unit": None, "price_per_sf": None,
        "noi_trailing": None, "noi_proforma": None,
        "cap_rate_trailing": None, "cap_rate_proforma": None,
        "occupancy_current": None, "occupancy_economic": None,
        "gross_revenue": None, "total_expenses": None, "expense_ratio": None,
    },
    "debt": {
        "ltv": None, "dscr": None, "interest_rate": None,
        "maturity_date": None, "assumable": None,
    },
    "leases": [],
    "extraction_flags": [],
}


def normalize_excel_output(raw: dict) -> dict:
    """
    Map parse_excel.py's flat output to partial ExtractedMetrics nested schema.
    Only maps fields that are present and non-null in the raw dict.
    Monthly values are annualized where the schema expects annual figures.
    """
    out = {"property": {}, "financials": {}, "debt": {}, "leases": [], "extraction_flags": []}

    # Property
    if raw.get("unit_count") is not None:
        out["property"]["units"] = raw["unit_count"]

    # Financials — annualize monthly values
    gross = raw.get("gross_income")
    if gross is not None:
        out["financials"]["gross_revenue"] = round(gross * 12, 2)

    expenses = raw.get("total_expenses")
    if expenses is not None:
        out["financials"]["total_expenses"] = round(expenses * 12, 2)

    noi = raw.get("noi_trailing_annualized") or raw.get("noi_trailing")
    if noi is not None:
        out["financials"]["noi_trailing"] = round(noi, 2)

    if raw.get("expense_ratio") is not None:
        out["financials"]["expense_ratio"] = raw["expense_ratio"]

    if raw.get("cap_rate_trailing") is not None:
        out["financials"]["cap_rate_trailing"] = raw["cap_rate_trailing"]

    occ = raw.get("occupancy_pct")
    if occ is not None:
        # parse_excel returns 100.0 for 100% — convert to decimal
        out["financials"]["occupancy_current"] = round(occ / 100, 4) if occ > 1 else occ

    # Debt
    if raw.get("loan_rate_weighted_avg") is not None:
        out["debt"]["interest_rate"] = raw["loan_rate_weighted_avg"]

    # Flags
    out["extraction_flags"] = raw.get("_extraction_flags", [])

    return out


def merge(excel: dict | None, claude: dict | None) -> tuple[dict, dict]:
    """
    Merge excel and claude metrics.
    Returns (merged_metrics, sources_dict).
    Excel wins on every field. Claude fills nulls.
    """
    merged = json.loads(json.dumps(EMPTY_METRICS))  # deep copy
    sources = {section: {} for section, _ in SCALAR_FIELDS}
    # de-dup sections
    sources = {}
    for section, field in SCALAR_FIELDS:
        sources.setdefault(section, {})[field] = None

    for section, field in SCALAR_FIELDS:
        excel_val = get_nested(excel, section, field) if excel else None
        claude_val = get_nested(claude, section, field) if claude else None

        if excel_val is not None:
            merged[section][field] = excel_val
            sources[section][field] = "excel"
        elif claude_val is not None:
            merged[section][field] = claude_val
            sources[section][field] = "claude"
        else:
            merged[section][field] = None
            sources[section][field] = None

    # Leases: prefer Excel if present, otherwise Claude
    excel_leases = (excel or {}).get("leases", [])
    claude_leases = (claude or {}).get("leases", [])
    merged["leases"] = excel_leases if excel_leases else claude_leases

    # Flags: combine both
    excel_flags = (excel or {}).get("extraction_flags", [])
    claude_flags = (claude or {}).get("extraction_flags", [])
    merged["extraction_flags"] = list(set(excel_flags + claude_flags))

    return merged, sources


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Merge Excel + Claude OM metrics")
    parser.add_argument("--raw-text", help="Path to raw PDF text file")
    parser.add_argument("--excel", help="Path to excel_metrics.json from parse_excel.py")
    parser.add_argument("--prompt", required=True, help="Path to om-extractor.md prompt")
    parser.add_argument("--out", required=True, help="Output path for extracted_metrics.json")
    args = parser.parse_args()

    if not args.raw_text and not args.excel:
        print("[merge_inputs] ERROR: at least one of --raw-text or --excel is required", file=sys.stderr)
        sys.exit(1)

    # Load prompt template
    with open(args.prompt, "r") as f:
        prompt_template = f.read()

    # Claude extraction (if PDF text available)
    claude_metrics = None
    if args.raw_text:
        if not os.path.exists(args.raw_text):
            print(f"[merge_inputs] ERROR: raw text file not found: {args.raw_text}", file=sys.stderr)
            sys.exit(1)
        with open(args.raw_text, "r") as f:
            raw_text = f.read()
        print(f"[merge_inputs] Calling Claude on {len(raw_text):,} chars of OM text...", file=sys.stderr)
        claude_metrics = call_claude(raw_text, prompt_template)
        print("[merge_inputs] Claude extraction complete.", file=sys.stderr)

    # Excel metrics (if available)
    excel_metrics = None
    if args.excel:
        if not os.path.exists(args.excel):
            print(f"[merge_inputs] ERROR: excel metrics file not found: {args.excel}", file=sys.stderr)
            sys.exit(1)
        raw_excel = load_json(args.excel)
        excel_metrics = normalize_excel_output(raw_excel)
        print(f"[merge_inputs] Loaded Excel metrics from {args.excel}", file=sys.stderr)

    # Merge
    merged, sources = merge(excel_metrics, claude_metrics)

    # Build final output
    output = {
        "deal_id": None,  # caller sets this
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        **merged,
        "_sources": sources,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, cls=DecimalEncoder)

    print(f"[merge_inputs] Written to {args.out}", file=sys.stderr)

    # Print field source summary to stdout
    filled = sum(
        1 for section, field in SCALAR_FIELDS
        if sources.get(section, {}).get(field) is not None
    )
    total = len(SCALAR_FIELDS)
    print(json.dumps({
        "fields_filled": filled,
        "fields_total": total,
        "fields_null": total - filled,
        "output": args.out,
    }))


if __name__ == "__main__":
    main()
