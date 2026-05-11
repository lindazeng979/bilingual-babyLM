#!/usr/bin/env python3
import json
import os
import sys
from tqdm import tqdm

# == Usage: python3 BL_training/scripts/preprocess_data/BL_json_to_text.py BL_training/data/exp BL_training/data/ready
def convert_jsonl_to_txt(input_file, output_file, field):
    """Convert a single JSONL file to TXT extracting only the specified field."""
    with open(output_file, "w", encoding="utf-8") as out:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in tqdm(f, desc=f"Converting {os.path.basename(input_file)}"):
                try:
                    entry = json.loads(line)
                    text = entry.get(field, "").strip()
                    if text:
                        out.write(text + "\n")
                except json.JSONDecodeError:
                    continue
    print(f"Saved {output_file}")

# === ENTRYPOINT ===
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python jsonl_to_txt.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    field = "content" 

    os.makedirs(output_dir, exist_ok=True)

    # Process each JSONL file separately
    input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".jsonl")]

    for input_file in input_files:
        base_name = os.path.splitext(os.path.basename(input_file))[0] + ".txt"
        output_file = os.path.join(output_dir, base_name)
        convert_jsonl_to_txt(input_file, output_file, field)