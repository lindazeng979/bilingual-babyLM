import json
import random
import os
import sys
import re
from tqdm import tqdm
random.seed(0)

# == Usage: python3 BL_training/scripts/preprocess_data/BL_combine_and_clean.py BL_collection_data/all/dadcommunity BL_training/data/clean/BL_dadcommunity_clean.jsonl
#Input: One directory with many json (i.e. all/momhome)
#Three preprocessing processes
#Combine within each directory 
#Output: One json file (all of the momhome)

#Repeat four times → Four files (momhome, dadhome, etc.) 25M data samples each

def filter_example(content):
    """Check if a dialogue is invalid. Works for English, Spanish, and Intersent."""
    lower_content = content.lower()

    # Keep text without headers as valid raw text (Spanish behavior is safer)
    if 'diálogo:' not in lower_content and 'dialogue:' not in lower_content:
        return False

    # Avoid multiple dialogue headers
    if lower_content.count('diálogo:') > 1 or lower_content.count('dialogue:') > 1:
        print("multiple dialogue headers")
        return True

    # Require bold speaker labels
    if '**' not in content:
        print("no bold speaker labels")
        return True

    # Limit overly long dialogues
    if len(content.split()) > 400:
        print("over line limit")
        return True

    return False

def normalize_labels(content):
    """Normalize speaker labels: Spanish → Mamá/Papá/Niño, English → Mom/Dad/Child."""
    # Variants
    mom_es_variants = ["Mamá", "Mama", "mamá", "mama", "Madre", "madre"]
    mom_en_variants = ["Mom", "mom", "Mother", "mother"]
    dad_es_variants = ["Papá", "Papa", "papá", "papa", "Padre", "padre"]
    dad_en_variants = ["Dad", "dad", "Father", "father"]
    child_es_variants = ["Niño", "Niña", "niño", "niña", "Hijo", "Hija", "hijo", "hija", "Adolescente", "adolescente"]
    child_en_variants = ["Child", "child", "Toddler", "toddler", "Teenager", "teenager"]

    # Normalize bold speaker labels
    for lbl in mom_es_variants:
        content = content.replace(f"**{lbl}**", "**Mamá**")
    for lbl in mom_en_variants:
        content = content.replace(f"**{lbl}**", "**Mom**")
    for lbl in dad_es_variants:
        content = content.replace(f"**{lbl}**", "**Papá**")
    for lbl in dad_en_variants:
        content = content.replace(f"**{lbl}**", "**Dad**")
    for lbl in child_es_variants:
        content = content.replace(f"**{lbl}**", "**Niño**")
    for lbl in child_en_variants:
        content = content.replace(f"**{lbl}**", "**Child**")

    # Normalize non-bold occurrences
    content = re.sub(r"\b(" + "|".join(mom_es_variants) + r")\b", "Mamá", content)
    content = re.sub(r"\b(" + "|".join(mom_en_variants) + r")\b", "Mom", content)
    content = re.sub(r"\b(" + "|".join(dad_es_variants) + r")\b", "Papá", content)
    content = re.sub(r"\b(" + "|".join(dad_en_variants) + r")\b", "Dad", content)
    content = re.sub(r"\b(" + "|".join(child_es_variants) + r")\b", "Niño", content)
    content = re.sub(r"\b(" + "|".join(child_en_variants) + r")\b", "Child", content)

    return content

def preprocess_content(content):
    """Preprocess dialogue text for any language without language detection."""
    content = content.strip()

    # Remove header
    if re.search(r"(diálogo:|dialogue:)", content, flags=re.IGNORECASE):
        content = re.sub(r"(?si)^.*?(diálogo:|dialogue:)\s*", "", content)

    # Normalize newlines
    content = content.replace("\n", "\\n").replace("\\n\\n", " \\n\\n ")
    if content.startswith("\\n"):
        content = content[2:]
    content = content.replace("\\n'\\n**", " \\n\\n **").replace("\\n**", " \\n\\n **")

    # Apply label normalization (Spanish + English)
    content = normalize_labels(content)

    # Standardize quotes
    content = (content.replace("’", "'")
                      .replace("‘", "'")
                      .replace("“", "\"")
                      .replace("”", "\""))

    # Append EOS token
    return content.strip() + " <|endoftext|>"

def combine_jsonl_files(input_files, output_file, txt_file):
    combined_data = []
    combined_dialogues = []
    kept = bad = total_words = 0

    for file_name in tqdm(input_files, desc="Processing files"):
        print(f"Processing {file_name}")
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    data = json.loads(line)
                    custom_id = data.get("custom_id", "")

                    # Extract original fields
                    en = data.get("content_en", "")
                    es = data.get("content_es", "")
                    inter = data.get("content_intersent", "")

                    # ✅ Apply filtering: if ANY field fails, mark as skipped
                    if (filter_example(en) or
                        filter_example(es) or
                        filter_example(inter)):
                        bad += 1
                        continue

                    # ✅ Preprocess each field
                    cleaned_en = preprocess_content(en)
                    cleaned_es = preprocess_content(es)
                    cleaned_inter = preprocess_content(inter)

                    kept += 1
                    total_words += (len(cleaned_en.split()) +
                                    len(cleaned_es.split()) +
                                    len(cleaned_inter.split()))

                    # ✅ Append cleaned entry
                    combined_data.append({
                        "custom_id": custom_id,
                        "content_en": cleaned_en,
                        "content_es": cleaned_es,
                        "content_intersent": cleaned_inter
                    })

                    # For TXT output, concatenate all three
                    # combined_dialogues.append(f"{cleaned_en} || {cleaned_es} || {cleaned_inter}")

                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON: {line.strip()}")
                    bad += 1
                    continue

    # === Summary ===
    print(f"\n{kept} examples kept")
    print(f"{bad} examples flagged as skipped")
    print(f"Total words: {total_words}")
    print(f"Avg words/example: {total_words / max(1, kept)}")

    # Randomize order
    #random.shuffle(combined_data)
    # random.shuffle(combined_dialogues)

    # === Save .txt (optional) ===
    # with open(txt_file, "w", encoding="utf-8") as f:
     #   for d in combined_dialogues:
     #       f.write(d + "\n")

    # === Save cleaned JSONL ===
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in combined_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

    print(f"Cleaned dataset saved to {output_file}")

