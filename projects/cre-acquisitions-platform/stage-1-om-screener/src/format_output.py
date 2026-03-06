"""
format_output.py — Generate narrative and format final screening output.

Takes scored results, generates Claude narrative, and assembles final ScreeningResult.

Usage:
    python3 src/format_output.py \
        --scored /tmp/deal_scored.json \
        --prompt prompts/om-narrator.md \
        --out output/DEAL_ID.json
"""

import argparse
import json
import sys
import os
import time
import pathlib
from datetime import datetime, timezone
from decimal import Decimal

import anthropic
from anthropic import APITimeoutError, RateLimitError
from dotenv import load_dotenv


def validate_input_path(path_str: str) -> str:
    """Validate that a file path exists and is readable."""
    try:
        path = pathlib.Path(path_str).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Not a file: {path}")
        return str(path)
    except (FileNotFoundError, ValueError):
        raise


def format_criteria_list(criteria_results: list, status: str) -> str:
    """Format criteria results for prompt context."""
    items = [r for r in criteria_results if r["result"] == status]
    if not items:
        return "None"
    return ", ".join([r["criterion"] for r in items])


def format_red_flags(red_flags: list) -> str:
    """Format red flags for prompt context."""
    if not red_flags:
        return "None"
    return "; ".join([f"{f['flag']}: {f['explanation']}" for f in red_flags])


def build_narrator_prompt(scored_result: dict, prompt_template: str) -> str:
    """
    Substitute variables into om-narrator.md prompt template.
    """
    metrics = scored_result.get("extracted_metrics", {})
    prop = metrics.get("property", {})
    fin = metrics.get("financials", {})
    debt = metrics.get("debt", {})
    criteria_results = scored_result.get("criteria_results", [])
    red_flags = scored_result.get("red_flags", [])
    
    # Format values for the prompt
    asking_price = fin.get("asking_price")
    asking_price_str = f"${asking_price:,.0f}" if asking_price else "N/A"
    
    cap_rate = fin.get("cap_rate_trailing")
    cap_rate_str = f"{cap_rate:.2%}" if cap_rate else "N/A"
    
    occupancy = fin.get("occupancy_current")
    occupancy_str = f"{occupancy:.1%}" if occupancy else "N/A"
    
    dscr = debt.get("dscr")
    dscr_str = f"{dscr:.2f}x" if dscr else "N/A"
    
    ltv = debt.get("ltv")
    ltv_str = f"{ltv:.1%}" if ltv else "N/A"
    
    exp_ratio = fin.get("expense_ratio")
    exp_ratio_str = f"{exp_ratio:.1%}" if exp_ratio else "N/A"
    
    passing = format_criteria_list(criteria_results, "PASS")
    flagged = format_criteria_list(criteria_results, "FLAG")
    
    # Substitute variables
    prompt = prompt_template
    prompt = prompt.replace("{{verdict}}", scored_result.get("verdict", "UNKNOWN"))
    prompt = prompt.replace("{{property_type}}", prop.get("type", "Unknown"))
    prompt = prompt.replace("{{market}}", prop.get("market", "Unknown"))
    prompt = prompt.replace("{{asking_price}}", asking_price_str)
    prompt = prompt.replace("{{cap_rate_trailing}}", cap_rate_str)
    prompt = prompt.replace("{{occupancy}}", occupancy_str)
    prompt = prompt.replace("{{dscr}}", dscr_str)
    prompt = prompt.replace("{{ltv}}", ltv_str)
    prompt = prompt.replace("{{expense_ratio}}", exp_ratio_str)
    prompt = prompt.replace("{{passing_criteria}}", passing)
    prompt = prompt.replace("{{flagged_criteria}}", flagged)
    prompt = prompt.replace("{{red_flags}}", format_red_flags(red_flags))
    
    return prompt


def call_claude_for_narrative(prompt: str, max_retries: int = 3) -> str:
    """
    Call Claude to generate the narrative summary with retry logic.
    
    Args:
        prompt: Prompt to send to Claude
        max_retries: Number of retry attempts for transient errors
    
    Returns:
        Generated narrative text
    
    Raises:
        Exception: If all retries fail or unrecoverable error occurs
    """
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                timeout=30.0,  # 30-second timeout per request
                messages=[{"role": "user", "content": prompt}],
            )
            
            narrative = message.content[0].text.strip()
            if attempt > 0:
                print(f"[format_output] Claude call succeeded on retry {attempt}", file=sys.stderr)
            return narrative
        
        except (APITimeoutError, RateLimitError) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(
                    f"[format_output] Claude API error (attempt {attempt + 1}/{max_retries}): {type(e).__name__}. "
                    f"Retrying in {wait_time}s...",
                    file=sys.stderr
                )
                time.sleep(wait_time)
            else:
                # All retries exhausted
                raise
        except Exception as e:
            # Unrecoverable error, don't retry
            raise


def main():
    parser = argparse.ArgumentParser(description="Generate narrative and format final screening output")
    parser.add_argument("--scored", required=True, help="Path to scoring_results.json from score.py")
    parser.add_argument("--prompt", required=True, help="Path to om-narrator.md")
    parser.add_argument("--out", required=True, help="Output path for final screening result JSON")
    args = parser.parse_args()
    
    # Load inputs
    try:
        scored_path = validate_input_path(args.scored)
        with open(scored_path, "r") as f:
            scored_result = json.load(f)
    except FileNotFoundError as e:
        print(f"[format_output] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[format_output] ERROR: Scored JSON parsing failed at line {e.lineno}, col {e.colno}: {e.msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[format_output] ERROR loading scored result: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        prompt_path = validate_input_path(args.prompt)
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
    except FileNotFoundError as e:
        print(f"[format_output] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[format_output] ERROR loading prompt: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load .env for API key
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    # Build narrator prompt
    try:
        narrator_prompt = build_narrator_prompt(scored_result, prompt_template)
    except Exception as e:
        print(f"[format_output] ERROR building narrator prompt: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Call Claude
    try:
        print("[format_output] Calling Claude for narrative...", file=sys.stderr)
        narrative = call_claude_for_narrative(narrator_prompt)
        print("[format_output] Narrative generated.", file=sys.stderr)
    except Exception as e:
        print(f"[format_output] ERROR calling Claude: {e}", file=sys.stderr)
        # Don't fail — just leave narrative empty
        narrative = "(Narrative generation failed)"
    
    # Add narrative to result
    scored_result["narrative"] = narrative
    scored_result["output_timestamp"] = datetime.now(timezone.utc).isoformat()
    
    # Write output
    try:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(scored_result, f, indent=2, cls=DecimalEncoder)
        print(f"[format_output] Final screening result written to {args.out}", file=sys.stderr)
    except Exception as e:
        print(f"[format_output] ERROR writing output: {e}", file=sys.stderr)
        sys.exit(1)


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder for Decimal types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


if __name__ == "__main__":
    main()
