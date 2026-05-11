#!/usr/bin/env python3

# Input an entire hierarchical folder of train and val jsons, output into a hierarchical folder of train and val txts

import json
import os
import sys

def extract_texts_from_file(json_file, txt_file):
    """Extract 'text' fields from a JSON/JSONL file into a TXT file."""
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(json_file, "r", encoding="utf-8") as f_in, \
         open(txt_file, "w", encoding="utf-8") as f_out:

        for line in f_in:
            line = line.strip()
            if not line:
                continue
            try:
                # JSONL style (one object per line)
                obj = json.loads(line)
                if isinstance(obj, dict) and "text" in obj:
                    f_out.write(obj["text"].replace("\n", " ") + "\n")
            except json.JSONDecodeError:
                try:
                    # maybe it's a big JSON array
                    data = json.loads(line)
                    if isinstance(data, list):
                        for obj in data:
                            if isinstance(obj, dict) and "text" in obj:
                                f_out.write(obj["text"].replace("\n", " ") + "\n")
                except:
                    continue

def process_directory(in_dir, out_dir="all_split_txt"):
    for root, dirs, files in os.walk(in_dir):
        for filename in files:
            if filename.endswith(".json") or filename.endswith(".jsonl"):
                json_path = os.path.join(root, filename)
                # build matching path inside out_dir
                rel_path = os.path.relpath(json_path, in_dir)
                txt_rel = os.path.splitext(rel_path)[0] + ".txt"
                txt_path = os.path.join(out_dir, txt_rel)

                print(f"Processing {rel_path} → {txt_rel}")
                extract_texts_from_file(json_path, txt_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_all.py <json_dir> [out_dir]")
        sys.exit(1)

    in_dir = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "all_split_txt"
    process_directory(in_dir, out_dir)
    print(f"All texts extracted to {out_dir}/")