#!/usr/bin/env python3
import json
import os
import random
import re
import sys
from tqdm import tqdm

#UNUSED
# == Usage: python3 BL_training/scripts/preprocess_data/BL_prepare_exp.py BL_training/data/clean BL_training/data/exp 
random.seed(0)

def load_jsonl_files(filepaths):
    data = []
    for path in filepaths:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    data.append(entry)
                except json.JSONDecodeError:
                    continue
    return data

def save_jsonl(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for d in data:
            json.dump(d, f, ensure_ascii=False)
            f.write("\n")
    print(f"Saved {len(data)} entries to {output_path}")

def extract_field(data, field):
    """Return dataset with only custom_id and the selected field renamed to 'content'."""
    return [{"custom_id": d.get("custom_id", ""), "content": d.get(field, "")} for d in data]

# === 2a: English Baseline & Topline ===
def prepare_english_baseline_topline(all_files, output_dir):
    data = load_jsonl_files(all_files)
    random.shuffle(data)

    # 50M → extract 12.5M per 4 categories
    baseline = extract_field(data[:12500000*4], "content_en")
    save_jsonl(baseline, os.path.join(output_dir, "english_baseline_50M.jsonl"))

    # 100M → extract all 25M
    topline = extract_field(data, "content_en")
    save_jsonl(topline, os.path.join(output_dir, "english_topline_100M.jsonl"))

# === 2b: By-Speaker & By-Context ===
def prepare_by_speaker_and_context(input_files, output_dir):
    """
    input_files: list of file paths (e.g., BL_dadcommunity_clean.jsonl)
    output_dir: where to save prepared files
    """
    # Map category to file
    file_map = {}
    for f in input_files:
        fname = os.path.basename(f).lower()
        if "momhome" in fname:
            file_map["momhome"] = f
        elif "momcommunity" in fname:
            file_map["momcommunity"] = f
        elif "dadhome" in fname:
            file_map["dadhome"] = f
        elif "dadcommunity" in fname:
            file_map["dadcommunity"] = f

    # Helper: choose correct field based on key suffix
    def get_field_from_key(key):
        return "content_es" if key.endswith("-spanish") else "content_en"

    def prepare_subset(keys, name):
        subset = []
        for key in keys:
            category = key.split("-")[0]  # momhome, momcommunity, etc.
            field = get_field_from_key(key)  # content_es or content_en
            file_path = file_map[category]
            # Load file and extract the correct language field
            data = load_jsonl_files([file_path])
            data_extracted = extract_field(data, field)
            subset.extend(data_extracted)

        random.shuffle(subset)
        save_jsonl(subset, os.path.join(output_dir, f"{name}_100M.jsonl"))

    # === Four combinations ===
    prepare_subset(
        ["momhome-spanish", "momcommunity-spanish", "dadhome-english", "dadcommunity-english"],
        "by-speaker-mom-spanish"
    )
    prepare_subset(
        ["momhome-english", "momcommunity-english", "dadhome-spanish", "dadcommunity-spanish"],
        "by-speaker-mom-english"
    )
    prepare_subset(
        ["momhome-spanish", "momcommunity-english", "dadhome-spanish", "dadcommunity-english"],
        "by-community-home-spanish"
    )
    prepare_subset(
        ["momhome-english", "momcommunity-spanish", "dadhome-english", "dadcommunity-spanish"],
        "by-community-home-english"
    )


# === 2c: Extract all Intersent Only ===
def prepare_intersent_only(all_files, output_dir):
    data = load_jsonl_files(all_files)
    random.shuffle(data)
    intersent = extract_field(data, "content_intersent")
    save_jsonl(intersent, os.path.join(output_dir, "all_intersent_100M.jsonl"))

# === 2d: Spanish Baseline & Topline ===
def prepare_spanish_baseline_topline(all_files, output_dir):
    data = load_jsonl_files(all_files)
    random.shuffle(data)

    baseline = extract_field(data[:12500000*4], "content_es")
    save_jsonl(baseline, os.path.join(output_dir, "spanish_baseline_50M.jsonl"))

    topline = extract_field(data, "content_es")
    save_jsonl(topline, os.path.join(output_dir, "spanish_topline_100M.jsonl"))

# === ENTRYPOINT ===
if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    all_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".jsonl")]


    # === Run all parts ===
    print("\nPreparing English Baseline & Topline (2a)")
    prepare_english_baseline_topline(all_files, output_dir)

    print("\nPreparing By-Speaker & By-Context (2b)")
    prepare_by_speaker_and_context(all_files, output_dir)

    print("\nPreparing Intersent Only (2c)")
    prepare_intersent_only(all_files, output_dir)

    print("\nPreparing Spanish Baseline & Topline (2d)")
    prepare_spanish_baseline_topline(all_files, output_dir)