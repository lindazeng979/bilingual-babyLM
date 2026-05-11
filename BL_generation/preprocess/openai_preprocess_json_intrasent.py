import json
import random
import os
import sys
import re
from tqdm import tqdm
random.seed(0)

# === OPTIONAL: ID FILTER ===

def load_allowed_ids(json_path):
    allowed = set()
    with open(json_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            allowed.add(data.get('custom_id'))
            #print(data.get('custom_id'))
    return allowed


def preprocess_mixed(content: str) -> str:
    """Preprocess dialogue content with correct dialogue marker handling."""

    original = content.strip()

    # ---------- FIXED DIALOGUE LOGIC ----------
    # Pattern for the dialogue markers (no inline flags here)
    dialogue_pattern = r"(DIALOGUE:|dialogue:|diálogo:|dialogo:)"

    # If it contains ANY dialogue marker, drop everything before+including the marker
    if re.search(dialogue_pattern, original, flags=re.IGNORECASE | re.DOTALL):
        content = re.sub(
            r"^.*?(DIALOGUE:|dialogue:|diálogo:|dialogo:)\s*",
            "",
            original,
            flags=re.IGNORECASE | re.DOTALL,
        )
    else:
        # Keep ENTIRE content unchanged (except subsequent normalization)
        content = original
        
    # Explicit newline tokens
    content = content.replace("\n", "\\n")

    # Ensure spaces around utterance separators
    content = content.replace("\\n\\n", " \\n\\n ")

    # Remove stray leading newline tokens
    if content.startswith("\\n"):
        content = content[2:]

    # Ensure utterance separator consistency
    content = (content.replace("\\n'\\n**", " \\n\\n **")
                      .replace("\\n**", " \\n\\n **"))

    # Fix colon placement: **Label:** → **Label**:
    content = re.sub(r"\*\*([^*]+):\*\*", r"**\1**:", content)

    # Normalize parent labels
    mom_variants = ["MOM","Mamá", "Mama", "mamá", "mama", "Madre", "madre", "Mom", "mom", "Mother", "mother"]
    dad_variants = ["DAD","Papá", "Papa", "papá", "papa", "Padre", "padre", "Dad", "dad", "Father", "father"]
    for lbl in mom_variants:
        content = content.replace(f"**{lbl}**", "**Mom**")
    for lbl in dad_variants:
        content = content.replace(f"**{lbl}**", "**Dad**")

    # Normalize child labels
    child_variants = [
        "Toddler", "toddler", "TODDLER",
        "Teenager", "teenager", "TEENAGER",
        "Niño", "Niña", "niño", "niña",
        "Hijo", "Hija", "hijo", "hija",
        "Adolescente", "adolescente", "Child", "child"
    ]
    for lbl in child_variants:
        content = content.replace(f"**{lbl}**", "**Child**")

    # Standardize quotes/apostrophes
    content = (content.replace("’", "'")
                      .replace("‘", "'")
                      .replace("“", "\"")
                      .replace("”", "\""))

    # Append EOS
    content = content.strip() + " <|endoftext|>"

    return content


def combine_jsonl_files(input_files, combined_jsonl_file, txt_file, allowed_ids=None):
    """
    If allowed_ids is provided (a set of 'blaabla'), keep an example only if:
    - data['custom_id'] exists,
    - starts with 'intrasent_',
    - and its suffix (after 'intrasent_') is in allowed_ids.
    """
    combined_data = []
    combined_dialogues = []
    kept = bad = total_words = 0
    filtered_out_by_id = 0

    for file_name in tqdm(input_files):
        print(f"Processing {file_name}")
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    data = json.loads(line)

                    # ==== ID FILTER HERE ====
                    if allowed_ids is not None:
                        custom_id = data.get("custom_id")
                        if not custom_id or not custom_id.startswith("intersent_"):
                            filtered_out_by_id += 1
                            continue
                        base_id = custom_id[len("intersent_"):]  # strip prefix
                        #print(base_id)
                        if base_id not in allowed_ids:
                            filtered_out_by_id += 1
                            continue
                    # =========================

                    content = (
                        data.get("response", {})
                            .get("body", {})
                            .get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "")
                    )

                    cleaned_content = preprocess_mixed(content)
                    kept += 1
                    total_words += len(cleaned_content.split())

                    combined_data.append(data)
                    combined_dialogues.append(cleaned_content)

                except json.JSONDecodeError:
                    print(f"Invalid JSON: {line.strip()}")
                    bad += 1

    print(f"\n{kept} examples kept (after ID + content filters)")
    print(f"{bad} examples flagged as skipped by filter_example")
    if allowed_ids is not None:
        print(f"{filtered_out_by_id} examples skipped because custom_id not in allowed_ids")

    print(f"\nTotal words: {total_words}")
    print(f"Avg words/example: {total_words / max(1, kept)}")

    # Shuffle consistently (independently)
    random.shuffle(combined_data)
    random.shuffle(combined_dialogues)

    # Save cleaned dialogues with placeholders
    with open(txt_file, 'w', encoding="utf-8") as f:
        for d in combined_dialogues:
            f.write(d + "\n")

    #Save combined JSONL with skip flags
    with open(combined_jsonl_file, 'w', encoding="utf-8") as f:
        for d in combined_data:
            json.dump(d, f, ensure_ascii=False)
            f.write("\n")

    print(len(combined_data))
    print("Intrasent GPT dataset processed and saved!")


# === ENTRYPOINT ===
# Usage:
#   python script.py input_folder output.jsonl output.txt [allowed_ids.json]
input_folder = sys.argv[1]
output_jsonl_file = sys.argv[2]
output_txt_file = sys.argv[3]

allowed_ids = None
if len(sys.argv) >= 5:
    id_filter_path = sys.argv[4]
    print(f"Loading allowed IDs from {id_filter_path}")
    allowed_ids = load_allowed_ids(id_filter_path)
    print(f"Loaded {len(allowed_ids)} allowed IDs")

input_files = [
    os.path.join(input_folder, f)
    for f in os.listdir(input_folder)
    if f.endswith(".jsonl")
]
print(f"Found {len(input_files)} files")

combine_jsonl_files(input_files, output_jsonl_file, output_txt_file, allowed_ids)

