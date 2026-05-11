#!/usr/bin/env python3
import sys
import json
import random
import re
from tqdm import tqdm
import nltk

nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize

USAGE = "Usage: python generate_intersent.py <english_jsonl> <spanish_jsonl> <out_intersent_jsonl> <out_all_jsonl>"

# --- CLI args ---
if len(sys.argv) != 5:
    print(USAGE)
    sys.exit(1)

english_path = sys.argv[1]
spanish_path = sys.argv[2]
out_intersent_path = sys.argv[3]
out_all_path = sys.argv[4]

def split_clauses(text, lang="english"):
    """Split text into sentences using NLTK."""
    # NLTK expects 'spanish' for Spanish
    return sent_tokenize(text, language=lang)

def split_clauses_regex(text):
    """Alternative regex-based clause splitter (unused by default)."""
    pattern = r"""
        (?<!\b\w{1,4})            # NOT preceded by short word
        (?<=[.!?…])               # End of sentence punctuation
        (?=\s+(?=["'¿¡A-Z]))      # Followed by capital, quote, etc.
        |
        \n{2,}                    # Or double newline
    """
    return [c.strip() for c in re.split(pattern, text, flags=re.VERBOSE) if c.strip()]

def generate_intersent(content_en, content_es, min_run=1, max_run=3):
    """Mix English and Spanish clauses randomly."""
    en_clauses = split_clauses(content_en, lang="english")
    es_clauses = split_clauses(content_es, lang="spanish")

    max_len = max(len(en_clauses), len(es_clauses))
    en_clauses += [""] * (max_len - len(en_clauses))
    es_clauses += [""] * (max_len - len(es_clauses))

    mixed, i, n = [], 0, max_len
    current_lang = random.choice(["en", "es"])
    run_length = random.randint(min_run, max_run)

    while i < n:
        for _ in range(run_length):
            if i >= n:
                break
            if current_lang == "en" and en_clauses[i]:
                mixed.append(en_clauses[i])
            elif current_lang == "es" and es_clauses[i]:
                mixed.append(es_clauses[i])
            i += 1
        current_lang = "es" if current_lang == "en" else "en"
        run_length = random.randint(min_run, max_run)

    return " ".join(mixed)

def load_spanish_dict(jsonl_path):
    """
    Load Spanish entries into a dict {custom_id: content_es}.
    Assumes OpenAI responses JSONL with structure used in your code.
    If custom_id starts with 'translate_', strip that prefix.
    """
    data = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            cid = obj.get("custom_id", "")
            if cid.startswith("translate_"):
                cid = cid[len("translate_"):]
            content_es = (
                obj.get("response", {})
                  .get("body", {})
                  .get("choices", [{}])[0]
                  .get("message", {})
                  .get("content", "")
            )
            if cid:
                data[cid] = content_es
    return data

def process_pair(english_jsonl, spanish_jsonl, out_intersent, out_all):
    print("Loading Spanish data...")
    spanish_data = load_spanish_dict(spanish_jsonl)
    print(f"Loaded {len(spanish_data)} Spanish entries.")

    # Read all English lines
    with open(english_jsonl, "r", encoding="utf-8") as infile:
        lines = [json.loads(line) for line in infile]

    intersent_lines = []
    all_lines = []
    skipped = 0

    for line in tqdm(lines, desc=f"Processing {english_jsonl}"):
        cid = line.get("custom_id", "")
        content_en = (
            line.get("response", {})
                .get("body", {})
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
        )
        content_es = spanish_data.get(cid, "")

        if not cid or not content_es:
            skipped += 1
            continue

        content_intersent = generate_intersent(content_en, content_es)

        intersent_lines.append({
            "custom_id": "intersent_" + cid,
            "content_intersent": content_intersent
        })

        all_lines.append({
            "custom_id": cid,
            "content_en": content_en,
            "content_es": content_es,
            "content_intersent": content_intersent
        })

    if not all_lines:
        print("⚠️ No matching entries found. Nothing to write.")
        return

    # Save intersent-only file
    with open(out_intersent, "w", encoding="utf-8") as out1:
        for obj in intersent_lines:
            out1.write(json.dumps(obj, ensure_ascii=False) + "\n")

    # Save ALL file
    with open(out_all, "w", encoding="utf-8") as out2:
        for obj in all_lines:
            out2.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"✅ Saved: {out_intersent} and {out_all} (Skipped {skipped})")

if __name__ == "__main__":
    process_pair(english_path, spanish_path, out_intersent_path, out_all_path)