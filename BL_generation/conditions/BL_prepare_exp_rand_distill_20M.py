# USED FOR REDUCED SIZE 20M (BASELINE_RANDOM_SPLIT CONDITION)
import json
import os

# base directories
base_input_dir = "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_exp_20M/random_split_20M"
base_output_dir = "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_exp_20M/baseline_random_split_20M"

splits = ["train", "val"]

for split in splits:
    print(f"\n=== Processing {split} ===")

    in_file = os.path.join(base_input_dir, f"{split}.jsonl")
    out_file = os.path.join(base_output_dir, f"{split}.jsonl")

    en_rows = []

    # 1. Load and filter
    with open(in_file, "r") as f:
        for line in f:
            row = json.loads(line)

            # filter English only
            if row.get("lang") == "en":
                en_rows.append(row)

    print(f"Loaded {len(en_rows)} English rows for {split}.")

    # 2. Save result
    with open(out_file, "w") as f:
        for row in en_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Saved EN-only file → {out_file}")