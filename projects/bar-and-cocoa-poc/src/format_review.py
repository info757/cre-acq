"""
Stage 3: Review Formatter
Bar & Cocoa POC — Triad AI

Takes the selection output from select.py and formats it as a 
clean, human-readable Markdown review message for Pashmina.
"""

import json
import sys
from pathlib import Path


def format_review(result: dict, today_str: str = None) -> str:
    import datetime
    if today_str is None:
        today_str = datetime.date.today().isoformat()

    bars = result["selected_bars"]
    meta = result["metadata"]
    summary = result.get("box_summary", "")

    lines = []
    lines.append("# 🍫 Bar & Cocoa — Gift Box Selection")
    lines.append(f"*Generated: {today_str}*\n")

    # Validation status
    if meta["valid"]:
        lines.append("**Status: ✅ All constraints satisfied — ready for review**\n")
    else:
        lines.append("**Status: ⚠️ CONSTRAINT VIOLATIONS — review required**")
        for v in meta["constraint_violations"]:
            lines.append(f"- ❌ {v}")
        lines.append("")

    # Box summary
    if summary:
        lines.append("## Box Overview")
        lines.append(summary)
        lines.append("")

    # Stats
    lines.append("## Box Stats")
    lines.append(f"- **Total price:** ${meta['total_price_usd']:.2f} USD")
    lines.append(f"- **Origins ({len(meta['distinct_origins'])}):** {', '.join(sorted(meta['distinct_origins']))}")
    lines.append(f"- **Types:** {', '.join(sorted(meta['types_included']))}")
    lines.append(f"- **Intensities:** {', '.join(sorted(meta['intensities_included']))}")
    lines.append("")

    # Bar-by-bar breakdown
    lines.append("## Selected Bars\n")

    # Group: flag borderline bars (low candidate score or close to expiry thresholds)
    borderline = []

    for i, bar in enumerate(bars, 1):
        score = bar.get("_candidate_score", 0)
        days_exp = bar.get("_days_until_expiry", "?")
        dos = bar.get("_days_of_supply")
        expiry_date = bar.get("expiry_date", "?")
        is_borderline = score < 0.5 or (isinstance(days_exp, int) and days_exp > 120)

        lines.append(f"### {i}. {bar['name']}")
        lines.append(f"**Maker:** {bar.get('maker', '?')} | **Origin:** {bar.get('origin', '?')} | **Type:** {bar.get('type', '?')} | **Cacao:** {bar.get('cacao_pct', '?')}%")
        lines.append(f"**Price:** ${bar.get('price_usd', 0):.2f} | **Intensity:** {bar.get('intensity', '?')}")
        lines.append(f"**Flavors:** {', '.join(bar.get('flavor_tags', []))}")
        lines.append(f"**Inventory:** {bar.get('current_inventory', '?')} units | **Velocity:** {bar.get('weekly_velocity', '?')}/wk | **Days of supply:** {f'{dos:.0f}d' if dos else '∞'}")
        lines.append(f"**Expires:** {expiry_date} ({days_exp} days) | **Candidate score:** {score:.3f}")

        if bar.get("dietary_flags"):
            lines.append(f"**Dietary:** {', '.join(bar['dietary_flags'])}")

        lines.append(f"\n> {bar.get('selection_reason', '')}")

        if is_borderline:
            borderline.append(bar["name"])
            lines.append("\n> ⚠️ *Borderline — review this pick*")

        lines.append("")

    # Borderline summary
    if borderline:
        lines.append("## ⚠️ Borderline Picks — Pashmina Should Review")
        for name in borderline:
            lines.append(f"- {name}")
        lines.append("")

    lines.append("---")
    lines.append("*Bar & Cocoa POC — Triad AI | Selection Agent v0.1*")

    return "\n".join(lines)


def load_selection(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    selection_path = base / "output" / "selection.json"

    if not selection_path.exists():
        print("No selection.json found. Run select.py first.")
        sys.exit(1)

    result = load_selection(selection_path)
    review = format_review(result)

    print(review)

    # Also write to file
    output_path = base / "output" / "review.md"
    with open(output_path, "w") as f:
        f.write(review)
    print(f"\n(Also saved to {output_path})")
