#!/usr/bin/env python3
import argparse, json, os, random
from collections import defaultdict, Counter
from math import floor

TARGET_CONDITIONS = ["momhome", "dadhome", "momcommunity", "dadcommunity"]
ALIASES = {
    "momcomm": "momcommunity",
    "dadcomm": "dadcommunity",
    "momcommunity": "momcommunity",
    "dadcommunity": "dadcommunity",
    "momhome": "momhome",
    "dadhome": "dadhome",
}

def infer_condition(rec):
    dom = (rec.get("domain") or "").strip().lower()
    if dom in ALIASES:
        return ALIASES[dom]
    cid = (rec.get("custom_id") or "").lower()
    for key in ALIASES:
        if key in cid:
            return ALIASES[key]
    return None

def build_master_idlist(reference_jsonl, out_path, val_pct_total=0.20, seed=42):
    random.seed(seed)
    groups = defaultdict(list)
    total = 0
    with open(reference_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            cond = infer_condition(rec)
            if cond in TARGET_CONDITIONS:
                groups[cond].append(rec)
            total += 1

    per_cond_val_target = floor(val_pct_total * total / len(TARGET_CONDITIONS))
    val_ids = set()
    for cond in TARGET_CONDITIONS:
        items = groups.get(cond, [])
        random.shuffle(items)
        n_val = min(per_cond_val_target, len(items))
        for r in items[:n_val]:
            cid = r.get("custom_id")
            if cid:
                val_ids.add(cid)

    # write master list
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for cid in sorted(val_ids):
            f.write(cid + "\n")

    # report
    report = {
        "reference_file": reference_jsonl,
        "total_rows_seen": total,
        "per_condition_counts": {c: len(groups.get(c, [])) for c in TARGET_CONDITIONS},
        "val_pct_total": val_pct_total,
        "per_condition_target": per_cond_val_target,
        "master_val_ids": len(val_ids),
    }
    return report

def load_idlist(path):
    ids = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                ids.add(s)
    return ids

def apply_master_to_file(input_jsonl, master_idlist_path, outdir, ids_only=False):
    os.makedirs(outdir, exist_ok=True)
    master_ids = load_idlist(master_idlist_path)

    paths = {
        "val": os.path.join(outdir, "val.jsonl"),
        "train": os.path.join(outdir, "train.jsonl"),
        "present_val_ids": os.path.join(outdir, "present_val_ids.txt"),
        "report": os.path.join(outdir, "apply_report.txt"),
    }

    present_val_ids = set()
    counts = {"val": Counter(), "train": Counter(), "unknown": 0}
    total = 0
    val_rows = train_rows = 0

    fw_val = None
    fw_train = None
    if not ids_only:
        fw_val = open(paths["val"], "w", encoding="utf-8")
        fw_train = open(paths["train"], "w", encoding="utf-8")

    with open(input_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = rec.get("custom_id")
            cond = infer_condition(rec) or "unknown"
            if cid in master_ids:
                present_val_ids.add(cid)
                if not ids_only:
                    fw_val.write(json.dumps(rec, ensure_ascii=False) + "\n")
                val_rows += 1
                counts["val"][cond] += 1
            else:
                if not ids_only:
                    fw_train.write(json.dumps(rec, ensure_ascii=False) + "\n")
                train_rows += 1
                counts["train"][cond] += 1

    if fw_val: fw_val.close()
    if fw_train: fw_train.close()

    # write present_val_ids list for this file
    with open(paths["present_val_ids"], "w", encoding="utf-8") as f:
        for cid in sorted(present_val_ids):
            f.write(cid + "\n")

    with open(paths["report"], "w", encoding="utf-8") as f:
        f.write(f"INPUT FILE: {input_jsonl}\n")
        f.write(f"MASTER ID LIST: {master_idlist_path}\n")
        f.write(f"TOTAL ROWS: {total}\n")
        f.write(f"VAL ROWS (intersection with master): {val_rows}\n")
        f.write(f"TRAIN ROWS: {train_rows}\n")
        f.write("\nBreakdown by condition (rows):\n")
        for split in ["val", "train"]:
            f.write(f"  {split}:\n")
            for cond in TARGET_CONDITIONS + ["unknown"]:
                f.write(f"    - {cond}: {counts[split][cond]}\n")

    return {
        "total_rows": total,
        "val_rows": val_rows,
        "train_rows": train_rows,
        "present_val_ids": len(present_val_ids),
    }

def main():
    ap = argparse.ArgumentParser(description="Consistent validation splits across multiple JSONLs using a master ID list.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build-master", action="store_true",
                      help="Build a master val ID list from a reference JSONL (5%% per condition, 20%% total).")
    mode.add_argument("--apply-master", action="store_true",
                      help="Apply an existing master val ID list to a JSONL and write val/train splits by intersection.")

    ap.add_argument("--reference", help="Reference JSONL when building the master list.")
    ap.add_argument("--master-out", help="Path to write the master val ID list (e.g., val_ids_master.txt).")
    ap.add_argument("--val-pct-total", type=float, default=0.20, help="Total fraction for validation when building master (default 0.20)")
    ap.add_argument("--seed", type=int, default=42, help="Sampling seed when building master")
    ap.add_argument("--input", help="Input JSONL when applying the master list.")
    ap.add_argument("--val-idlist", help="Existing master val ID list to apply.")
    ap.add_argument("--outdir", help="Output directory when applying the master list.")
    ap.add_argument("--ids-only", action="store_true", help="Only write ID list when applying (skip JSONL splits).")

    args = ap.parse_args()

    if args.build_master:
        if not args.reference or not args.master_out:
            raise SystemExit("--reference and --master-out are required with --build-master")
        report = build_master_idlist(args.reference, args.master_out, args.val_pct_total, args.seed)
        print("Built master ID list at:", args.master_out)
        for k, v in report.items():
            print(f"{k}: {v}")
    elif args.apply_master:
        if not args.input or not args.val_idlist or not args.outdir:
            raise SystemExit("--input, --val-idlist, and --outdir are required with --apply-master")
        stats = apply_master_to_file(args.input, args.val_idlist, args.outdir, ids_only=args.ids_only)
        print("Applied master to:", args.input)
        for k, v in stats.items():
            print(f"{k}: {v}")

if __name__ == "__main__":
    main()
