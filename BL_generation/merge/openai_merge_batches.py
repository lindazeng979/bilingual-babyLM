#!/usr/bin/env python3
"""
Combine batch folders into a single 'combined' tree without deleting the originals.

Expected source layout (repeated per batchN*):
  batchX/
    momcommunity/
      inputs/    metadata/    outputs/    mapping.txt
    momhome/
      inputs/    metadata/    outputs/    mapping.txt
    dadcommunity/
      inputs/    metadata/    outputs/    mapping.txt
    dadhome/
      inputs/    metadata/    outputs/    mapping.txt

This script creates:
  combined/
    momcommunity/{inputs,metadata,outputs}/   (merged contents)
    momhome/{inputs,metadata,outputs}/
    dadcommunity/{inputs,metadata,outputs}/
    dadhome/{inputs,metadata,outputs}/
    mapping.txt                      (global concatenation of *all* mapping.txts)
    momcommunity_mapping.txt         (per-category concatenation)
    momhome_mapping.txt
    dadcommunity_mapping.txt
    dadhome_mapping.txt
"""

import shutil
from pathlib import Path
import sys

# --- Config ---
CATEGORIES = ["momcommunity", "momhome", "dadcommunity", "dadhome"]
SUBS = ["inputs", "metadata", "outputs"]
ROOT = "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data" #Path(".").resolve()
DEST = "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/english"

# Normalize to Path
ROOT = Path(ROOT).resolve()
DEST = Path(DEST).resolve()

def iter_batch_dirs(root: Path):
    # any dir starting with 'batch' counts
    for p in sorted(root.iterdir()):
        if p.is_dir() and p.name.lower().startswith("batch"):
            yield p

def ensure_dirs():
    for cat in CATEGORIES:
        for sub in SUBS:
            (DEST / cat / sub).mkdir(parents=True, exist_ok=True)

def unique_dest_path(dest_dir: Path, rel_name: str, batch_name: str) -> Path:
    """
    If rel_name already exists in dest_dir, prefix with batch name.
    If still collides, add an incrementing suffix.
    """
    candidate = dest_dir / rel_name
    if not candidate.exists():
        return candidate
    # Try batch-prefixed
    candidate = dest_dir / f"{batch_name}__{rel_name}"
    if not candidate.exists():
        return candidate
    # Add numeric suffix
    stem = candidate.stem
    suffix = candidate.suffix
    i = 1
    while True:
        c = dest_dir / f"{stem}__{i}{suffix}"
        if not c.exists():
            return c
        i += 1

def copy_tree_contents(src_dir: Path, dest_dir: Path, batch_name: str):
    """
    Copy *files* from src_dir into dest_dir, recursively.
    Keeps relative subpaths; if a file would collide, it’s renamed.
    """
    if not src_dir.exists():
        return
    for p in src_dir.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src_dir)
            # ensure intermediate folders exist in dest
            target_parent = dest_dir / rel.parent
            target_parent.mkdir(parents=True, exist_ok=True)
            target = target_parent / rel.name
            if target.exists():
                # resolve collision at the leaf filename only
                target = unique_dest_path(target_parent, rel.name, batch_name)
            shutil.copy2(p, target)

def append_mapping(mapping_src: Path, global_out: Path, category_out: Path, batch_name: str, category: str):
    if not mapping_src.exists():
        return
    header = f"# --- from {batch_name}/{category}/mapping.txt ---\n"
    text = mapping_src.read_text(encoding="utf-8", errors="ignore")
    # Append to global
    with global_out.open("a", encoding="utf-8") as g:
        g.write(header)
        g.write(text)
        if not text.endswith("\n"):
            g.write("\n")
    # Append to per-category
    with category_out.open("a", encoding="utf-8") as c:
        c.write(header)
        c.write(text)
        if not text.endswith("\n"):
            c.write("\n")

def main():
    DEST.mkdir(exist_ok=True)
    ensure_dirs()

    global_mapping = DEST / "mapping.txt"
    # Clear existing combined mapping files if re-running
    if global_mapping.exists():
        global_mapping.unlink()
    per_cat_mapping = {cat: DEST / f"{cat}_mapping.txt" for cat in CATEGORIES}
    for f in per_cat_mapping.values():
        if f.exists():
            f.unlink()

    batches = list(iter_batch_dirs(ROOT))
    if not batches:
        print("No batch* directories found. Run this from the parent of your batch folders.")
        sys.exit(1)

    for b in batches:
        batch_name = b.name
        for cat in CATEGORIES:
            cat_dir = b / cat
            if not cat_dir.exists():
                # skip silently if a category is missing in a batch
                continue
            # copy subfolders
            for sub in SUBS:
                src = cat_dir / sub
                dest = DEST / cat / sub
                copy_tree_contents(src, dest, batch_name=batch_name)
            # mapping
            append_mapping(
                mapping_src=cat_dir / "mapping.txt",
                global_out=global_mapping,
                category_out=per_cat_mapping[cat],
                batch_name=batch_name,
                category=cat,
            )

    print(f"Done.\nCombined output: {DEST}\n- Global mapping: {global_mapping}\n- Per-category mappings: {', '.join(str(p) for p in per_cat_mapping.values())}")

if __name__ == "__main__":
    main()