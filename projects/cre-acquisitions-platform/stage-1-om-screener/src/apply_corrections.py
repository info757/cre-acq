"""
apply_corrections.py — Apply human corrections to extracted metrics.

After format_review_message.py displays metrics, the user can reply with corrections.
This script takes those corrections and applies them to extracted_metrics.json,
outputting confirmed_metrics.json.

User correction formats:
  "ok" → no corrections, pass through extracted_metrics.json unchanged
  "fix: field value" → update specific field with new value
    Example: "fix: asking_price 42500000"

Usage:
    python3 src/apply_corrections.py \
        --metrics /tmp/deal_extracted.json \
        --corrections "<user response>" \
        --out /tmp/deal_confirmed.json

Or with structured JSON corrections:
    python3 src/apply_corrections.py \
        --metrics /tmp/deal_extracted.json \
        --corrections '{"field_name": "value", ...}' \
        --out /tmp/deal_confirmed.json
"""

import argparse
import json
import sys
import re
from copy import deepcopy
from decimal import Decimal


# Field path mappings (field_name -> [section, key])
# Allows both "occupancy_current" and "occupancy__current" styles
FIELD_MAPPING = {
    # Property fields
    "property_type": ("property", "type"),
    "type": ("property", "type"),
    "property_market": ("property", "market"),
    "market": ("property", "market"),
    "property_submarket": ("property", "submarket"),
    "submarket": ("property", "submarket"),
    "property_address": ("property", "address"),
    "address": ("property", "address"),
    "property_vintage": ("property", "vintage"),
    "vintage": ("property", "vintage"),
    "property_units": ("property", "units"),
    "units": ("property", "units"),
    "property_total_sf": ("property", "total_sf"),
    "total_sf": ("property", "total_sf"),
    
    # Financial fields
    "asking_price": ("financials", "asking_price"),
    "price_per_unit": ("financials", "price_per_unit"),
    "price_per_sf": ("financials", "price_per_sf"),
    "noi_trailing": ("financials", "noi_trailing"),
    "noi_proforma": ("financials", "noi_proforma"),
    "cap_rate_trailing": ("financials", "cap_rate_trailing"),
    "cap_rate_proforma": ("financials", "cap_rate_proforma"),
    "occupancy_current": ("financials", "occupancy_current"),
    "occupancy_economic": ("financials", "occupancy_economic"),
    "gross_revenue": ("financials", "gross_revenue"),
    "total_expenses": ("financials", "total_expenses"),
    "expense_ratio": ("financials", "expense_ratio"),
    
    # Debt fields
    "ltv": ("debt", "ltv"),
    "dscr": ("debt", "dscr"),
    "interest_rate": ("debt", "interest_rate"),
    "maturity_date": ("debt", "maturity_date"),
    "assumable": ("debt", "assumable"),
}


def coerce_value(field_name: str, raw_value: str):
    """
    Coerce a string value to the appropriate Python type.
    
    Rules:
    - "true" / "false" (case-insensitive) → boolean
    - Numeric strings that look like percentages (0.05, 0.88) → float
    - Numeric strings → int or float depending on context
    - Everything else → string
    """
    val = raw_value.strip()
    
    # Boolean
    if val.lower() in ("true", "yes"):
        return True
    if val.lower() in ("false", "no"):
        return False
    
    # Try numeric
    try:
        # If it contains a decimal point, float
        if "." in val:
            return float(val)
        # Otherwise try int first, fall back to float
        return int(val)
    except ValueError:
        pass
    
    # Otherwise keep as string
    return val


def resolve_field_path(field_name: str) -> tuple:
    """
    Resolve a field name to (section, key).
    Handles:
      - "occupancy_current" (direct field name)
      - "property_occupancy_current" (section_field)
      - "financials_asking_price" (section_field)
    """
    # Direct lookup
    if field_name in FIELD_MAPPING:
        return FIELD_MAPPING[field_name]
    
    # Try section_field pattern: property_units, financials_asking_price, etc.
    for section in ("property", "financials", "debt"):
        prefix = f"{section}_"
        if field_name.startswith(prefix):
            key = field_name[len(prefix):]
            if key in FIELD_MAPPING and FIELD_MAPPING[key][0] == section:
                return FIELD_MAPPING[key]
    
    # If not found, raise error
    raise ValueError(f"Unknown field: {field_name}")


def apply_text_correction(metrics: dict, correction_text: str) -> dict:
    """
    Parse and apply a single text-based correction.
    Format: "fix: field_name value"
    
    Example: "fix: asking_price 42500000"
    """
    metrics = deepcopy(metrics)
    
    # Remove common prefixes
    text = correction_text.strip()
    if text.lower().startswith("fix:"):
        text = text[4:].strip()
    
    # Split on first space: "field_name value"
    parts = text.split(None, 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid correction format: {correction_text}. Expected 'fix: field_name value'")
    
    field_name, value_str = parts
    
    # Resolve field path
    try:
        section, key = resolve_field_path(field_name)
    except ValueError as e:
        raise ValueError(f"Invalid field in correction: {e}")
    
    # Coerce value
    value = coerce_value(field_name, value_str)
    
    # Apply
    if section not in metrics:
        metrics[section] = {}
    metrics[section][key] = value
    
    return metrics


def apply_json_corrections(metrics: dict, corrections_dict: dict) -> dict:
    """
    Apply corrections from a dict of {field_name: value} pairs.
    """
    metrics = deepcopy(metrics)
    
    for field_name, value in corrections_dict.items():
        try:
            section, key = resolve_field_path(field_name)
        except ValueError as e:
            print(f"[apply_corrections] Warning: {e}, skipping", file=sys.stderr)
            continue
        
        if section not in metrics:
            metrics[section] = {}
        metrics[section][key] = value
    
    return metrics


def parse_corrections_input(corrections_str: str) -> dict | list[str] | None:
    """
    Parse the corrections input (could be JSON, text, or null).
    
    Returns:
      - dict: if JSON with {field: value} structure
      - list[str]: if multiple "fix:" commands separated by newlines
      - None: if "ok" (no corrections)
    """
    corrections_str = corrections_str.strip()
    
    # Empty or "ok" → no corrections
    if not corrections_str or corrections_str.lower() == "ok":
        return None
    
    # Try parsing as JSON
    try:
        parsed = json.loads(corrections_str)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    
    # Treat as text commands: split on newlines
    lines = [line.strip() for line in corrections_str.split("\n") if line.strip()]
    if lines:
        return lines
    
    return None


def main():
    parser = argparse.ArgumentParser(description="Apply human corrections to extracted metrics")
    parser.add_argument("--metrics", required=True, help="Path to extracted_metrics.json")
    parser.add_argument("--corrections", required=True, help="Correction string (text or JSON)")
    parser.add_argument("--out", required=True, help="Output path for confirmed_metrics.json")
    args = parser.parse_args()
    
    # Load extracted metrics
    try:
        with open(args.metrics, "r") as f:
            metrics = json.load(f)
    except Exception as e:
        print(f"[apply_corrections] ERROR loading metrics: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse corrections input
    try:
        corrections = parse_corrections_input(args.corrections)
    except Exception as e:
        print(f"[apply_corrections] ERROR parsing corrections: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Apply corrections
    try:
        if corrections is None:
            # No corrections, pass through
            confirmed = metrics
            print("[apply_corrections] No corrections provided, passing through extracted metrics", file=sys.stderr)
        elif isinstance(corrections, dict):
            # JSON dict of {field: value}
            confirmed = apply_json_corrections(metrics, corrections)
            print(f"[apply_corrections] Applied {len(corrections)} JSON corrections", file=sys.stderr)
        elif isinstance(corrections, list):
            # List of "fix: field value" commands
            confirmed = metrics
            for correction_text in corrections:
                confirmed = apply_text_correction(confirmed, correction_text)
                print(f"[apply_corrections]   Applied: {correction_text}", file=sys.stderr)
    except Exception as e:
        print(f"[apply_corrections] ERROR applying corrections: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write confirmed metrics
    try:
        with open(args.out, "w") as f:
            json.dump(confirmed, f, indent=2, cls=DecimalEncoder)
        print(f"[apply_corrections] Confirmed metrics written to {args.out}", file=sys.stderr)
    except Exception as e:
        print(f"[apply_corrections] ERROR writing output: {e}", file=sys.stderr)
        sys.exit(1)


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


if __name__ == "__main__":
    main()
