import os
import json
import sys
import re
from tqdm import tqdm

# ✅ Usage:
# python prepare_translation_batch.py <input_dir> <output_dir> <model_name>
# Example:
# python prepare_translation_batch.py BL_collection_data/english/momhome/inputs BL_collection_data/spanish/momhome/inputs gpt-4o-mini-2024-07-18

if len(sys.argv) < 4:
    print("Usage: python prepare_translation_batch.py <input_dir> <output_dir> <model_name>")
    sys.exit(1)

input_dir = sys.argv[1]
output_dir = sys.argv[2]
model_deployment_name = sys.argv[3]

os.makedirs(output_dir, exist_ok=True)

def prepare_translation_prompt(text_en):
    """Create GPT-4o batch API request body for translating text_en to Spanish."""
    return {
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model_deployment_name,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Translate the following English text (beginning at the word ‘PARTICIPANTS’) into Spanish while preserving its meaning and tone. "
                        "Do not add explanations or comments. Output only the translated text.\n\n"
                        f"{text_en}"
                    )
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }
    }

def clean_custom_id(custom_id):
    """Remove the '_ex-<number>' part from the custom_id."""
    return re.sub(r"_ex-\d+$", "", custom_id)

def process_file(input_path, output_path):
    """Reads input JSONL, extracts text, and writes GPT-4o batch API requests."""
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = [json.loads(line) for line in infile]

    print(f"📄 Processing {os.path.basename(input_path)} with {len(lines)} entries")

    with open(output_path, "w", encoding="utf-8") as outfile:
        for line in tqdm(lines):
            content_en = line["response"]["body"]["choices"][0]["message"]["content"]
            original_custom_id = line.get("custom_id", "no_id")

            # ✅ Preserve original custom_id in each request
            batch_entry = {
                "custom_id": f"translate_{original_custom_id}",
                **prepare_translation_prompt(content_en)
            }

            outfile.write(json.dumps(batch_entry, ensure_ascii=False) + "\n")

    print(f"✅ Finished: {output_path}")

# 🔷 Process all JSONL files
for fname in os.listdir(input_dir):
    if fname.endswith(".jsonl"):
        input_path = os.path.join(input_dir, fname)

        # ✅ Read first line to derive output file name from its custom_id
        with open(input_path, "r", encoding="utf-8") as f:
            first_line = json.loads(f.readline())
            base_custom_id = clean_custom_id(first_line.get("custom_id", "unknown"))

        output_fname = f"translate_{base_custom_id}.jsonl"
        output_path = os.path.join(output_dir, output_fname)

        process_file(input_path, output_path)

print("\n🎯 All GPT-4o translation batch files created successfully.")