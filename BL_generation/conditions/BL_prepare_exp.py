# USED FOR MAIN EXPERIMENT (ALL EXCEPT BASELINE_RANDOM_SPLIT, RANDOM_SPLIT, INTRASENT CONDITIONS)

from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

LANG_KEYS = {
    "en": "content_en",
    "es": "content_es",
    "intersent": "content_intersent",
}

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


def write_jsonl(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    total_words = 0
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
            total_words += len(r["text"].split())
    print(f"Wrote {n:,} lines → {out_path}")
    print(f"Total words in {out_path.name}: {total_words:,}")


# -------- Building mixes --------

def build_custom_mix(input_dir: Path, name: str, comps: list[str], seed: int | None, max_total: int | None, shuffle: bool = False):
    """comps are strings like 'dadhome:en' (up to four)."""
    parts = []
    for comp in comps:
        if ":" not in comp:
            raise ValueError(f"Component must look like DOMAIN:LANG, got '{comp}'")
        domain, lang = comp.split(":", 1)
        domain = domain.strip()
        lang = lang.strip().lower()
        rows = load_component(input_dir, domain, lang)
        parts.extend(rows)

    if shuffle:
        rnd = random.Random(seed)
        rnd.shuffle(parts)

    if max_total is not None and len(parts) > max_total:
        parts = parts[:max_total]

    return name, parts


def build_random_english(input_dir: Path, name: str, seed: int | None, max_total: int | None, shuffle: bool = False):
    all_rows = []
    for domain in ["dadhome","momhome","dadcomm","momcomm"]:
        all_rows.extend(load_component(input_dir, domain, "en"))

    if shuffle:
        rnd = random.Random(seed)
        rnd.shuffle(all_rows)

    if max_total is not None and len(all_rows) > max_total:
        all_rows = all_rows[:max_total]

    return name, all_rows

def count_words(content):
    return len(content.split())

# -------- CLI --------

def main():
    ap = argparse.ArgumentParser(description="Simple 4-way corpus mixer")
    ap.add_argument("--input_dir", type=Path, required=True)
    ap.add_argument("--out_dir", type=Path, required=True)

    # One custom mix (optional)
    ap.add_argument("--make_mix", type=str, default=None, help="Name for the custom mix output (e.g., fam_mix)")
    ap.add_argument("--comp", action="append", default=[], help="Repeat up to 4 times: DOMAIN:LANG (e.g., dadhome:en)")

    # One random-English mix (optional)
    ap.add_argument("--make_random_english", type=str, default=None, help="Name for the random English output (e.g., english_all)")

    # Common quality-of-life flags
    ap.add_argument("--shuffle", action="store_true", help="Shuffle examples before writing")
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
            max_total=args.max_total,
        )
        write_jsonl(rows, out_dir / f"{name}.jsonl")

    # Random English mix
    if args.make_random_english:
        name, rows = build_random_english(
            input_dir=args.input_dir,
            name=args.make_random_english,
            shuffle=bool(args.shuffle),
            seed=args.seed,
            max_total=args.random_max_total,
        )
        write_jsonl(rows, out_dir / f"{name}.jsonl")

    print("Done.")


if __name__ == "__main__":
    main()


'''
python3 BL_generation/BL_prepare_exp.py \
  --input_dir BL_collection_data/all_downsampled \
  --out_dir BL_collection_data/all_experiments \
  --make_mix eng_topline \
  --comp dadhome:en \
  --comp momhome:en \
  --comp dadcomm:en \
  --comp momcomm:en \
  --shuffle --seed 42 --max_total 710,772

python3 BL_generation/BL_prepare_exp.py \
  --input_dir BL_collection_data/all_downsampled \
  --out_dir BL_collection_data/all_experiments \
  --make_mix sp_topline \
  --comp dadhome:en \
  --comp momhome:en \
  --comp dadcomm:en \
  --comp momcomm:en \
  --shuffle --seed 42 --max_total 100000000


python3 BL_generation/BL_prepare_exp.py \
  --input_dir BL_collection_data/all_downsampled \
  --out_dir BL_collection_data/all_experiments \
  --make_random_english eng_baseline \
  --shuffle --seed 42 --random_max_total 355386
  
  '''