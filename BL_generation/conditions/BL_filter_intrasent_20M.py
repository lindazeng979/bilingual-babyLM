# USED FOR REDUCED SIZE 20M (INTRASENT CONDITION)
import json
import os

# base directories
base_split_dir = "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_exp_20M/intersent_20M"
second_file    = "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/intrasent/intrasent.jsonl"
out_dir        = "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_exp_20M/intrasent_20M"

splits = ["train", "val"]

for split in splits:
    print(f"\n=== Processing {split} ===")

    first_file = os.path.join(base_split_dir, f"{split}.jsonl")
    out_file   = os.path.join(out_dir, f"{split}.jsonl")

    # 1. Load valid IDs from first file
    valid_ids = set()

    with open(first_file, "r") as f:
        for line in f:
            row = json.loads(line)
            cid = row.get("custom_id")
            if cid:
                valid_ids.add(cid)

    print(f"Loaded {len(valid_ids)} valid custom_ids from {split} file.")

    # 2. Filter second file
    kept = []

    with open(second_file, "r") as f:
        for line in f:
            row = json.loads(line)
            cid = row.get("custom_id")
            if not cid:
                continue

            # remove prefix if present
            base_id = cid.replace("intersent_", "")

            if base_id in valid_ids:
                kept.append(row)

    print(f"Filtered: kept {len(kept)} rows for {split}.")

    # 3. Save result
    with open(out_file, "w") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Saved → {out_file}")