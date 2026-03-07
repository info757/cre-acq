"""
format_review_message.py — Format ExtractedMetrics for Telegram human review.

Takes extracted_metrics.json (output from merge_inputs.py), formats as readable
Telegram message with source tags (Excel / Claude / missing).

Usage:
    python3 src/format_review_message.py --metrics /tmp/deal_extracted.json

Output: formatted Telegram message string to stdout.
         (n8n Node 6 captures this and sends to Telegram.)
"""

import argparse
import json
import sys
import pathlib


def format_money(val):
    """Format a number as currency."""
    if val is None:
        return "—"
    if isinstance(val, str):
        return val
    return f"${val:,.0f}"


def format_percent(val):
    """Format a number as percentage."""
    if val is None:
        return "—"
    if isinstance(val, str):
        return val
    # If it's already decimal (0.88), multiply by 100
    if val < 1:
        return f"{val * 100:.1f}%"
    # If it's already percent (88), use as-is
    return f"{val:.1f}%"


def format_number(val):
    """Format a plain number."""
    if val is None:
        return "—"
    if isinstance(val, str):
        return val
    if isinstance(val, float):
        return f"{val:,.1f}"
    return f"{val:,}"


def source_tag(sources, section, field):
    """Return source indicator: [EXCEL], [CLAUDE], or [?] for missing."""
    if not sources:
        return ""
    section_sources = sources.get(section, {})
    source = section_sources.get(field)
    if source == "excel":
        return " [EXCEL]"
    elif source == "claude":
        return " [CLAUDE]"
    else:
        return " [?]"


def format_extracted_metrics(metrics: dict) -> str:
    """
    Format ExtractedMetrics JSON as a human-readable Telegram message.
    Includes source tags for each field.
    """
    sources = metrics.get("_sources", {})
    msg = []

    msg.append("🏢 *EXTRACTION REVIEW*\n")
    msg.append(f"Deal ID: {metrics.get('deal_id', 'unset')}\n")

    # ========== PROPERTY ==========
    msg.append("\n*PROPERTY*")
    prop = metrics.get("property", {})

    if prop.get("type") is not None:
        msg.append(f"  Type: {prop['type']}{source_tag(sources, 'property', 'type')}")
    if prop.get("market") is not None:
        msg.append(f"  Market: {prop['market']}{source_tag(sources, 'property', 'market')}")
    if prop.get("submarket") is not None:
        msg.append(f"  Submarket: {prop['submarket']}{source_tag(sources, 'property', 'submarket')}")
    if prop.get("address") is not None:
        msg.append(f"  Address: {prop['address']}{source_tag(sources, 'property', 'address')}")
    if prop.get("vintage") is not None:
        msg.append(f"  Built: {prop['vintage']}{source_tag(sources, 'property', 'vintage')}")
    if prop.get("units") is not None:
        msg.append(f"  Units: {format_number(prop['units'])}{source_tag(sources, 'property', 'units')}")
    if prop.get("total_sf") is not None:
        msg.append(f"  Total SF: {format_number(prop['total_sf'])}{source_tag(sources, 'property', 'total_sf')}")

    # ========== FINANCIALS ==========
    msg.append("\n*FINANCIALS*")
    fin = metrics.get("financials", {})

    if fin.get("asking_price") is not None:
        msg.append(f"  Asking Price: {format_money(fin['asking_price'])}{source_tag(sources, 'financials', 'asking_price')}")
    if fin.get("price_per_unit") is not None:
        msg.append(f"  $/Unit: {format_money(fin['price_per_unit'])}{source_tag(sources, 'financials', 'price_per_unit')}")
    if fin.get("price_per_sf") is not None:
        msg.append(f"  $/SF: {format_money(fin['price_per_sf'])}{source_tag(sources, 'financials', 'price_per_sf')}")
    if fin.get("gross_revenue") is not None:
        msg.append(f"  Gross Revenue: {format_money(fin['gross_revenue'])}{source_tag(sources, 'financials', 'gross_revenue')}")
    if fin.get("total_expenses") is not None:
        msg.append(f"  Total Expenses: {format_money(fin['total_expenses'])}{source_tag(sources, 'financials', 'total_expenses')}")
    if fin.get("noi_trailing") is not None:
        msg.append(f"  NOI (Trailing): {format_money(fin['noi_trailing'])}{source_tag(sources, 'financials', 'noi_trailing')}")
    if fin.get("noi_proforma") is not None:
        msg.append(f"  NOI (Pro Forma): {format_money(fin['noi_proforma'])}{source_tag(sources, 'financials', 'noi_proforma')}")
    if fin.get("cap_rate_trailing") is not None:
        msg.append(f"  Cap Rate (Trailing): {format_percent(fin['cap_rate_trailing'])}{source_tag(sources, 'financials', 'cap_rate_trailing')}")
    if fin.get("cap_rate_proforma") is not None:
        msg.append(f"  Cap Rate (Pro Forma): {format_percent(fin['cap_rate_proforma'])}{source_tag(sources, 'financials', 'cap_rate_proforma')}")
    if fin.get("occupancy_current") is not None:
        msg.append(f"  Occupancy (Current): {format_percent(fin['occupancy_current'])}{source_tag(sources, 'financials', 'occupancy_current')}")
    if fin.get("occupancy_economic") is not None:
        msg.append(f"  Occupancy (Economic): {format_percent(fin['occupancy_economic'])}{source_tag(sources, 'financials', 'occupancy_economic')}")
    if fin.get("expense_ratio") is not None:
        msg.append(f"  Expense Ratio: {format_percent(fin['expense_ratio'])}{source_tag(sources, 'financials', 'expense_ratio')}")

    # ========== DEBT ==========
    msg.append("\n*DEBT*")
    debt = metrics.get("debt", {})

    if debt.get("ltv") is not None:
        msg.append(f"  LTV: {format_percent(debt['ltv'])}{source_tag(sources, 'debt', 'ltv')}")
    if debt.get("dscr") is not None:
        msg.append(f"  DSCR: {format_number(debt['dscr'])}{source_tag(sources, 'debt', 'dscr')}")
    if debt.get("interest_rate") is not None:
        msg.append(f"  Interest Rate: {format_percent(debt['interest_rate'])}{source_tag(sources, 'debt', 'interest_rate')}")
    if debt.get("maturity_date") is not None:
        msg.append(f"  Maturity: {debt['maturity_date']}{source_tag(sources, 'debt', 'maturity_date')}")
    if debt.get("assumable") is not None:
        msg.append(f"  Assumable: {'Yes' if debt['assumable'] else 'No'}{source_tag(sources, 'debt', 'assumable')}")

    # ========== LEASES ==========
    leases = metrics.get("leases", [])
    if leases:
        msg.append("\n*TOP LEASES*")
        for i, lease in enumerate(leases[:5], 1):  # Show top 5
            tenant = lease.get("tenant", "Unknown")
            sf = lease.get("sf")
            expiration = lease.get("expiration", "N/A")
            msg.append(f"  {i}. {tenant} | {format_number(sf)} SF | Exp: {expiration}")

    # ========== FLAGS ==========
    flags = metrics.get("extraction_flags", [])
    if flags:
        msg.append("\n*⚠️  EXTRACTION FLAGS*")
        for flag in flags:
            msg.append(f"  • {flag}")

    msg.append("\n*CONFIRM METRICS:*")
    msg.append("  Reply 'ok' to proceed to scoring.")
    msg.append("  Reply 'fix: <field> <value>' to correct a field before scoring.")
    msg.append("  Example: 'fix: asking_price 42500000'")

    return "\n".join(msg)


def validate_input_path(path_str: str) -> str:
    """
    Validate that a file path exists and is readable.
    
    Args:
        path_str: File path provided by user
    
    Returns:
        Validated absolute path
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is inaccessible
    """
    try:
        path = pathlib.Path(path_str).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Not a file: {path}")
        return str(path)
    except (FileNotFoundError, ValueError):
        raise


def main():
    parser = argparse.ArgumentParser(description="Format ExtractedMetrics for Telegram review")
    parser.add_argument("--metrics", required=True, help="Path to extracted_metrics.json")
    args = parser.parse_args()

    try:
        # Validate path exists and is accessible
        metrics_path = validate_input_path(args.metrics)
        
        # Read and parse JSON
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        
        # Format and output
        msg = format_extracted_metrics(metrics)
        print(msg)
    
    except FileNotFoundError as e:
        print(f"[format_review_message] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[format_review_message] ERROR: JSON parsing failed at line {e.lineno}, col {e.colno}: {e.msg}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"[format_review_message] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
