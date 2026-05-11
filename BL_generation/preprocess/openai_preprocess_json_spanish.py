import json
import random
import os
import sys
import re
from tqdm import tqdm
random.seed(0)

#merge batches within one folder and preprocess

def preprocess_mixed(content: str) -> str:
    """Preprocess dialogue content that may be in English, Spanish, or a mix."""

    content = content.strip()

    # Remove everything before (and including) the first occurrence of dialogue marker
    content = re.sub(r"(?si)^.*?(DIALOGUE:|dialogue:|diálogo:|dialogo:)\s*", "", content)

    # Explicit newline tokens
    content = content.replace("\n", "\\n")

    # Ensure spaces before and after double newlines (utterance separators)
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
    mom_variants = ["Mamá", "Mama", "mamá", "mama", "Madre", "madre", "Mom", "mom", "Mother", "mother"]
    dad_variants = ["Papá", "Papa", "papá", "papa", "Padre", "padre", "Dad", "dad", "Father", "father"]
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

    # Append EOS token
    content = content.strip() + " <|endoftext|>"

    return content


def combine_jsonl_files(input_files, combined_jsonl_file, txt_file):
    combined_data = []
    combined_dialogues = []
    kept = bad = total_words = 0

    for file_name in tqdm(input_files):
        print(f"Processing {file_name}")
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    data = json.loads(line)
                    content = data.get("response", {}).get("body", {}).get("choices", [{}])[0].get("message", {}).get("content", "")

                    # ✅ If filtering fails, keep placeholder instead of skipping
                    if filter_example(content):
                        bad += 1
                        #combined_data.append({**data, "skipped": True})
                        #combined_dialogues.append("<SKIPPED_EXAMPLE>")
                        continue

                    cleaned_content = preprocess_mixed(content)
                    kept += 1
                    total_words += len(cleaned_content.split())

                    combined_data.append(data)
                    combined_dialogues.append(cleaned_content)

                except json.JSONDecodeError:
                    print(f"Invalid JSON: {line.strip()}")
                    bad += 1
                    #combined_dialogues.append("<SKIPPED_EXAMPLE>")

    print(f"\n{kept} examples kept")
    print(f"{bad} examples flagged as skipped")
    print(f"\nTotal words: {total_words}")
    print(f"Avg words/example: {total_words / max(1, kept)}")

    random.shuffle(combined_data)
    random.shuffle(combined_dialogues)

    # Save cleaned dialogues with placeholders
    with open(txt_file, 'w', encoding="utf-8") as f:
        for d in combined_dialogues:
            f.write(d + "\n")

    # Save combined JSONL with skip flags
    with open(combined_jsonl_file, 'w', encoding="utf-8") as f:
        for d in combined_data:
            json.dump(d, f, ensure_ascii=False)
            f.write("\n")

    print(len(combined_data))
    print("Intrasent GPT dataset processed and saved!")


# === ENTRYPOINT ===
input_folder = sys.argv[1]
output_jsonl_file = sys.argv[2]
output_txt_file = sys.argv[3]

input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".jsonl")]
print(f"Found {len(input_files)} files")
combine_jsonl_files(input_files, output_jsonl_file, output_txt_file)