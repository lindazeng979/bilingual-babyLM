# USED FOR REDUCED SIZE 20M EXPERIMENTS (ALL EXCEPT BASELINE_RANDOM_SPLIT, RANDOM_SPLIT, INTRASENT CONDITIONS)

from __future__ import annotations
import argparse
import json
import random
import re
from pathlib import Path
from typing import List, Tuple

LANG_KEYS = {
    "en": "content_en",
    "es": "content_es",
    "intersent": "content_intersent",
}

WORD_RE = re.compile(r"\S+")

# -------- Helpers --------

def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

def take_first_n(rows, n, shuffle, seed):
    if shuffle:
        rnd = random.Random(seed)
        rnd.shuffle(rows)
    return rows[:n]

def load_component(input_dir: Path, domain: str, lang: str):
    """Return list of {custom_id, text, lang, domain} for one DOMAIN:LANG."""
    key = LANG_KEYS.get(lang)
    if key is None:
        raise ValueError(f"Language must be one of {list(LANG_KEYS)}, got {lang}")
    src = input_dir / f"BL_{domain}_test_outputs.jsonl"
    if not src.exists():
        raise FileNotFoundError(f"Can't find {src}")

    rows = []
    for obj in iter_jsonl(src):
        text = obj.get(key) or ""
        if not text:
            continue
        rows.append({
            "custom_id": obj.get("custom_id"),
            "text": text,
            "lang": lang,
            "domain": domain,
        })
    return rows

def count_words(s: str) -> int:
    # Matches whitespace-delimited tokens; mirrors your previous split() but faster
    return len(WORD_RE.findall(s))

def write_jsonl(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    total_words = 0
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
            total_words += count_words(r["text"])
    print(f"Wrote {n:,} lines → {out_path}")
    print(f"Total words in {out_path.name}: {total_words:,}")

# -------- Selection logic --------

# -------- Building mixes --------
def build_custom_mix(
    input_dir: Path,
    name: str,
    comps: list[str],
    seed: int | None,
    shuffle: bool,
    lines_per_component: int
):
    parts = []
    for comp in comps:
        domain, lang = comp.split(":", 1)
        rows = load_component(input_dir, domain.strip(), lang.strip().lower())
        selected = take_first_n(rows, lines_per_component, shuffle, seed)
        print(f"[{domain}:{lang}] kept {len(selected):,} lines")
        parts.extend(selected)
    return name, parts

def build_random_english(
    input_dir: Path,
    name: str,
    seed: int | None,
    shuffle: bool,
    lines_per_component: int
):
    all_rows = []
    for domain in ["dadhome","momhome","dadcomm","momcomm"]:
        rows = load_component(input_dir, domain, "en")
        selected = take_first_n(rows, lines_per_component, shuffle, seed)
        print(f"[{domain}:en] kept {len(selected):,} lines")
        all_rows.extend(selected)
    return name, all_rows

# -------- CLI --------

def main():
    ap = argparse.ArgumentParser(description="Simple 4-way corpus mixer (per-component word budgets supported)")
    ap.add_argument("--input_dir", type=Path, required=True)
    ap.add_argument("--out_dir", type=Path, required=True)

    # One custom mix (optional)
    ap.add_argument("--make_mix", type=str, default=None, help="Name for the custom mix output (e.g., fam_mix)")
    ap.add_argument("--comp", action="append", default=[], help="Repeat up to 4 times: DOMAIN:LANG (e.g., dadhome:en)")
    ap.add_argument("--lines_per_component", type=int, required=True)
    ap.add_argument("--strict_words", action="store_true", help="If set, truncate the last sample to hit the word budget exactly")

    # One random-English mix (optional)
    ap.add_argument("--make_random_english", type=str, default=None, help="Name for the random English output (e.g., english_all)")
    ap.add_argument("--random_lines_total", type=int, default=None, help="If set, cap the random-English mix to this many words")

    # Common quality-of-life flags
    ap.add_argument("--shuffle", action="store_true", help="Shuffle examples before selection/writing")
    ap.add_argument("--seed", type=int, default=123, help="Random seed when --shuffle is used")
    ap.add_argument("--max_total", type=int, default=None, help="Cap total lines in the custom mix")
    ap.add_argument("--random_max_total", type=int, default=None, help="Cap total lines in the random-English mix")

    args = ap.parse_args()
    out_dir: Path = args.out_dir

    # Custom 4-part mix
    if args.make_mix:
        if not args.comp:
            raise SystemExit("You gave --make_mix but no --comp. Add components like --comp dadhome:en")
        if len(args.comp) > 4:
            raise SystemExit("Please provide at most 4 --comp entries.")
        name, rows = build_custom_mix(
            input_dir=args.input_dir,
            name=args.make_mix,
            comps=args.comp,
            shuffle=bool(args.shuffle),
            seed=args.seed,
            lines_per_component=args.lines_per_component,
        )
        write_jsonl(rows, out_dir / f"{name}.jsonl")

    # Random English mix
    if args.make_random_english:
        name, rows = build_random_english(
            input_dir=args.input_dir,
            name=args.make_random_english,
            shuffle=bool(args.shuffle),
            seed=args.seed,
            lines_per_component=args.lines_per_component,
        )
        write_jsonl(rows, out_dir / f"{name}.jsonl")

    print("Done.")

if __name__ == "__main__":
    main()