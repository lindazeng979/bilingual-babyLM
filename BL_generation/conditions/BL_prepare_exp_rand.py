# USED FOR "VARYING EXPOSURE PROPORTION" EXPERIMENTS
# ALSO USED FOR MAIN EXPERIMENT (RANDOM_SPLIT CONDITION)

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

DOMAINS = ["dadhome", "momhome", "dadcomm", "momcomm"]

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
    print(out_path)
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

def build_custom_mix(input_dir: Path, name: str, comps: list[str],
                     seed: int | None, max_total: int | None,
                     shuffle: bool = False):
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


def build_random_english(input_dir: Path, name: str,
                         seed: int | None, max_total: int | None,
                         shuffle: bool = False):
    all_rows = []
    for domain in DOMAINS:
        all_rows.extend(load_component(input_dir, domain, "en"))

    if shuffle:
        rnd = random.Random(seed)
        rnd.shuffle(all_rows)

    if max_total is not None and len(all_rows) > max_total:
        all_rows = all_rows[:max_total]

    return name, all_rows

# -------- Unbalanced EN–ES mix (probabilistic) --------
def build_mixed_en_es(input_dir: Path, name: str,
                      seed: int | None,
                      p_es: float = 0.5,          # <-- choose how much ES
                      shuffle: bool = False):
    """
    For ids where both EN and ES exist:
      choose ES with probability p_es, else EN.
    For ids with only one language: keep what's available.
    """
    assert 0.0 <= p_es <= 1.0, "p_es must be between 0 and 1"
    rnd = random.Random(seed)

    by_id: dict[str, dict[str, dict]] = {}

    for domain in DOMAINS:
        for lang in ("en", "es"):
            rows = load_component(input_dir, domain, lang)
            for row in rows:
                cid = row.get("custom_id")
                if not cid:
                    continue
                by_id.setdefault(cid, {})[lang] = row

    ids = list(by_id.keys())
    if shuffle:
        rnd.shuffle(ids)

    chosen_rows = []
    n_en = 0
    n_es = 0

    for cid in ids:
        langs = by_id[cid]

        if "en" in langs and "es" in langs:
            # ES with probability p_es
            if rnd.random() < p_es:
                chosen = langs["es"]; n_es += 1
            else:
                chosen = langs["en"]; n_en += 1
        elif "en" in langs:
            chosen = langs["en"]; n_en += 1
        elif "es" in langs:
            chosen = langs["es"]; n_es += 1
        else:
            continue

        chosen_rows.append(chosen)

    if shuffle:
        rnd.shuffle(chosen_rows)

    print(f"Per-id EN/ES mix: {len(chosen_rows):,} total, {n_en:,} EN, {n_es:,} ES (p_es={p_es})")
    return name, chosen_rows


    # -------- Unbalanced EN–ES mix (probabilistic) --------
def build_mixed_en_es_nospanish(input_dir: Path, name: str,
                      seed: int | None,
                      p_es: float = 0.5,          # <-- choose how much ES
                      shuffle: bool = False):
    """
    For ids where both EN and ES exist:
      choose ES with probability p_es, else EN.
    For ids with only one language: keep what's available.
    """
    assert 0.0 <= p_es <= 1.0, "p_es must be between 0 and 1"
    rnd = random.Random(seed)

    by_id: dict[str, dict[str, dict]] = {}

    for domain in DOMAINS:
        for lang in ("en", "es"):
            rows = load_component(input_dir, domain, lang)
            for row in rows:
                cid = row.get("custom_id")
                if not cid:
                    continue
                by_id.setdefault(cid, {})[lang] = row

    ids = list(by_id.keys())
    if shuffle:
        rnd.shuffle(ids)

    chosen_rows = []
    n_en = 0
    n_es = 0

    for cid in ids:
        langs = by_id[cid]

        if "en" in langs and "es" in langs:
            # ES with probability p_es
            if rnd.random() < p_es:
                continue
            else:
                chosen = langs["en"]; n_en += 1
        elif "en" in langs:
            chosen = langs["en"]; n_en += 1
        elif "es" in langs:
            continue
        else:
            continue

        chosen_rows.append(chosen)

    if shuffle:
        rnd.shuffle(chosen_rows)

    print(f"Per-id EN/ES mix: {len(chosen_rows):,} total, {n_en:,} EN, {n_es:,} ES (p_es={p_es})")
    return name, chosen_rows


# -------- Balanced EN–ES mix --------
def build_balanced_en_es(input_dir: Path, name: str,
                         seed: int | None, max_per_lang: int | None,
                         shuffle: bool = False):
    """
    For each custom_id across the four domains, randomly choose EN or ES
    (preferring pairs where both exist), so that every id appears exactly once.

    The result is a single mixed list of rows with roughly 50/50 EN–ES.
    max_per_lang is IGNORED here to ensure all ids are kept.
    """
    rnd = random.Random(seed)

    # custom_id -> {"en": row, "es": row}
    by_id: dict[str, dict[str, dict]] = {}

    for domain in DOMAINS:
        for lang in ("en", "es"):
            rows = load_component(input_dir, domain, lang)
            for row in rows:
                cid = row.get("custom_id")
                if not cid:
                    continue
                slot = by_id.setdefault(cid, {})
                # If there are duplicates, the last one wins; adjust if you prefer first one
                slot[lang] = row

    ids = list(by_id.keys())
    if shuffle:
        rnd.shuffle(ids)

    chosen_rows = []
    n_en = 0
    n_es = 0

    for cid in ids:
        langs = by_id[cid]

        if "en" in langs and "es" in langs:
            choice = rnd.choice(["en", "es"])
            chosen = langs[choice]
            if choice == "en":
                n_en += 1
            else:
                n_es += 1
        elif "en" in langs:
            # Only EN available for this id
            chosen = langs["en"]
            n_en += 1
        elif "es" in langs:
            # Only ES available for this id
            chosen = langs["es"]
            n_es += 1
        else:
            # Shouldn't happen, but be defensive
            continue

        chosen_rows.append(chosen)

    # Final shuffle of the mixed rows so EN/ES are interleaved
    if shuffle:
        rnd.shuffle(chosen_rows)

    print(
        f"Random per-id EN/ES: {len(chosen_rows):,} ids total, "
        f"{n_en:,} EN, {n_es:,} ES"
    )
    if max_per_lang is not None:
        print(
            f"[info] max_per_lang={max_per_lang} is ignored to keep ALL ids; "
            f"total is fixed at number of unique custom_id."
        )

    return name, chosen_rows


def count_words(content):
    return len(content.split())

# -------- CLI --------

def main():
    ap = argparse.ArgumentParser(description="Simple 4-way corpus mixer")
    ap.add_argument("--input_dir", type=Path, required=True)
    ap.add_argument("--out_dir", type=Path, required=True)

    # One custom mix (optional)
    ap.add_argument("--make_mix", type=str, default=None,
                    help="Name for the custom mix output (e.g., fam_mix)")
    ap.add_argument("--comp", action="append", default=[],
                    help="Repeat up to 4 times: DOMAIN:LANG (e.g., dadhome:en)")

    # One random-English mix (optional)
    ap.add_argument("--make_random_english", type=str, default=None,
                    help="Name for the random English output (e.g., english_all)")

    # Balanced EN–ES mix (optional)
    ap.add_argument("--make_balanced_en_es", type=str, default=None,
                    help="Base name for balanced EN/ES outputs (e.g., balanced_topline "
                         "→ balanced_topline_en.jsonl and balanced_topline_es.jsonl)")
    ap.add_argument("--make_mixed_en_es", type=str, default=None,
                    help="Base name for balanced EN/ES outputs (e.g., balanced_topline "
                         "→ balanced_topline_en.jsonl and balanced_topline_es.jsonl)")
    ap.add_argument("--make_mixed_en_es_nosp", type=str, default=None,
                    help="Base name for balanced EN/ES outputs (e.g., balanced_topline "
                         "→ balanced_topline_en.jsonl and balanced_topline_es.jsonl)")
    ap.add_argument("--balanced_max_per_lang", type=int, default=None,
                    help="Cap per-language lines in the balanced EN–ES mix "
                         "(total lines = 2 × this number)")

    # Common quality-of-life flags
    ap.add_argument("--shuffle", action="store_true",
                    help="Shuffle examples before writing")
    ap.add_argument("--seed", type=int, default=123,
                    help="Random seed when --shuffle is used")

    ap.add_argument("--mixing_proportion", type=float, default=0.5,
                    help="Random seed when --shuffle is used")

    ap.add_argument("--max_total", type=int, default=None,
                    help="Cap total lines in the custom mix")
    ap.add_argument("--random_max_total", type=int, default=None,
                    help="Cap total lines in the random-English mix")

    args = ap.parse_args()

    out_dir: Path = args.out_dir

    # Custom 4-part mix
    if args.make_mix:
        if not args.comp:
            raise SystemExit("You gave --make_mix but no --comp. "
                             "Add components like --comp dadhome:en")
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

    # Balanced EN–ES mix
    if args.make_balanced_en_es:
        (name_en, en_rows) = build_balanced_en_es(
            input_dir=args.input_dir,
            name=args.make_balanced_en_es,
            shuffle=bool(args.shuffle),
            seed=args.seed,
            max_per_lang=args.balanced_max_per_lang,
        )
        write_jsonl(en_rows, out_dir / f"{name_en}.jsonl")
    
    if args.make_mixed_en_es:
        (name_en, en_rows) = build_mixed_en_es(
            input_dir=args.input_dir,
            name=args.make_mixed_en_es,
            shuffle=bool(args.shuffle),
            seed=args.seed,
            p_es=args.mixing_proportion,
        )
        write_jsonl(en_rows, out_dir / f"{name_en}.jsonl")

    if args.make_mixed_en_es_nosp:
        (name_en, en_rows) = build_mixed_en_es_nospanish(
            input_dir=args.input_dir,
            name=args.make_mixed_en_es_nosp,
            shuffle=bool(args.shuffle),
            seed=args.seed,
            p_es=args.mixing_proportion,
        )
        write_jsonl(en_rows, out_dir / f"{name_en}.jsonl")

    print("Done.")


if __name__ == "__main__":
    main()