"""
format_valuation_output.py — Assemble ValuationResult and generate narrative.

Usage:
    python3 src/format_valuation_output.py \
        --valuation-input path \
        --direct-cap 35065501 \
        --dcf-result path \
        --flags path \
        --prompt prompts/valuation-narrator.md \
        --out output/deal_valuation.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(_):
        pass


def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def call_claude_narrative(prompt: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        return f"(Narrative generation skipped: {e})"


def build_prompt(vi: dict, direct_cap: float, dcf_result: dict, flags: list) -> str:
    template_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "valuation-narrator.md")
    with open(template_path, "r") as f:
        tpl = f.read()
    fin = vi.get("screening_result", {}).get("extracted_metrics", {}).get("financials", {})
    overrides = vi.get("valuation_overrides", {})
    asking = fin.get("asking_price") or 0
    returns = dcf_result.get("returns", {})
    tpl = tpl.replace("{{direct_cap_value}}", f"${direct_cap:,.0f}")
    tpl = tpl.replace("{{dcf_value}}", f"${dcf_result.get('dcf_value', 0):,.0f}")
    tpl = tpl.replace("{{asking_price}}", f"${asking:,.0f}")
    tpl = tpl.replace("{{irr}}", f"{returns.get('irr', 0):.1%}")
    tpl = tpl.replace("{{equity_multiple}}", f"{returns.get('equity_multiple', 0):.2f}x")
    tpl = tpl.replace("{{assumptions}}", json.dumps(overrides, indent=0)[:500])
    tpl = tpl.replace("{{flags}}", json.dumps(flags) if flags else "None")
    return tpl


def main():
    parser = argparse.ArgumentParser(description="Format valuation output with narrative")
    parser.add_argument("--valuation-input", required=True)
    parser.add_argument("--direct-cap", type=float, required=True)
    parser.add_argument("--dcf-result", required=True)
    parser.add_argument("--flags", required=True)
    parser.add_argument("--prompt", help="Path to valuation-narrator.md (optional)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    # Load .env: stage-1 has ANTHROPIC_API_KEY; stage-2 and project root can override
    _stage2 = Path(__file__).resolve().parent.parent
    _project = _stage2.parent
    _stage1 = _project / "stage-1-om-screener"
    for p in [_stage1 / ".env", _project / ".env", _stage2 / ".env"]:
        if p.exists():
            load_dotenv(p)

    vi = load_json(args.valuation_input)
    dcf_result = load_json(args.dcf_result)
    with open(args.flags, "r") as f:
        flags = json.load(f) if os.path.getsize(args.flags) > 0 else []

    prompt = build_prompt(vi, args.direct_cap, dcf_result, flags)
    try:
        narrative = call_claude_narrative(prompt)
    except Exception as e:
        narrative = f"(Narrative generation failed: {e})"

    screening = vi.get("screening_result", {})
    deal_id = screening.get("deal_id", "unknown")
    asking = screening.get("extracted_metrics", {}).get("financials", {}).get("asking_price") or 0
    dcf_val = dcf_result.get("dcf_value", 0)
    suggested = min(args.direct_cap, dcf_val) * 0.98  # Slight discount for offer

    result = {
        "deal_id": deal_id,
        "valued_at": datetime.now(timezone.utc).isoformat(),
        "direct_cap_value": args.direct_cap,
        "dcf_value": dcf_val,
        "suggested_offer": round(suggested, 2),
        "suggested_offer_note": "~2% below lower of direct cap/DCF value",
        "returns": dcf_result.get("returns", {}),
        "sensitivity": dcf_result.get("sensitivity", {}),
        "assumptions": vi.get("valuation_overrides", {}),
        "flags": flags,
        "narrative": narrative,
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

    msg = f"""VALUATION — {deal_id}
Direct Cap: ${args.direct_cap:,.0f}
DCF: ${dcf_val:,.0f}
Suggested Offer: ${suggested:,.0f}
IRR: {result['returns'].get('irr', 0):.1%} | Equity Multiple: {result['returns'].get('equity_multiple', 0):.2f}x

{narrative}
"""
    print(msg)


if __name__ == "__main__":
    main()
