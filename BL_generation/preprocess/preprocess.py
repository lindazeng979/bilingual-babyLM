import json
import re
import sys
from tqdm import tqdm
import os


FORBIDDEN_MARKERS = [
    "SETTING:", "DIALOGUE:", "DIALOGO:", "DIÁLOGO:", "ESCENARIO:", "PARTICIPANTES:", "PARTICIPANTS:"
]

def contains_forbidden_marker(text: str) -> bool:
    """Check if text contains any forbidden markers in caps."""
    for marker in FORBIDDEN_MARKERS:
        if marker in text:  # exact uppercase check
            return True
    return False
    
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

    # Append EOS token
    content = content.strip() + " <|endoftext|>"

    return content
def process_all(json_file: str, out_dir: str, passthrough_on_error: bool = False):
    total_examples = 0
    total_en = 0
    total_es = 0
    total_inter = 0
    malformed_count = 0

    # Prepare output
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, os.path.basename(json_file))

    with open(json_file, "r", encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out:
        for line in tqdm(f, desc="Processing"):
            line = line.rstrip("\n")

            try:
                obj = json.loads(line)

                en_raw = obj.get("content_en", "")
                es_raw = obj.get("content_es", "")
                inter_raw = obj.get("content_intersent", "")

                en_proc = preprocess_mixed(en_raw)
                es_proc = preprocess_mixed(es_raw) 
                inter_proc = preprocess_mixed(inter_raw)

                # If any forbidden marker exists in raw fields, drop this whole object
                if (contains_forbidden_marker(en_proc) or contains_forbidden_marker(es_proc) or
                    contains_forbidden_marker(inter_proc)):
                    malformed_count += 1
                    continue

                obj["content_en"] = en_proc
                obj["content_es"] = es_proc
                obj["content_intersent"] = inter_proc

                # Word counts
                wc_en = len(en_proc.split())
                wc_es = len(es_proc.split())
                wc_inter = len(inter_proc.split())

                total_examples += 1
                total_en += wc_en
                total_es += wc_es
                total_inter += wc_inter

                out.write(json.dumps(obj, ensure_ascii=False) + "\n")

            except json.JSONDecodeError:
                malformed_count += 1
                if passthrough_on_error and line.strip():
                    # Preserve original line unmodified so nothing is dropped
                    out.write(line + "\n")
                # else: skip truly empty lines

    avg_en = (total_en / total_examples) if total_examples else 0.0
    avg_es = (total_es / total_examples) if total_examples else 0.0
    avg_inter = (total_inter / total_examples) if total_examples else 0.0

    print(f"Examples processed (valid JSON): {total_examples}")
    print(f"Malformed lines encountered: {malformed_count}{' (preserved)' if passthrough_on_error else ' (skipped)'}")
    print(f"English:  total {total_en}, avg {avg_en:.2f}")
    print(f"Spanish:  total {total_es}, avg {avg_es:.2f}")
    print(f"Intersent: total {total_inter}, avg {avg_inter:.2f}")
    print(f"Saved preprocessed file to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 /Users/lindazeng/Documents/bilingual-llms/BL_generation/preprocess.py <json_file> <out_dir>")
        sys.exit(1)

    json_file = sys.argv[1]
    # Keep CLI stable but ignore remove_n to avoid dropping data
    out_dir = sys.argv[2]

    #print("[note] remove_n argument is ignored to ensure no data points are dropped.")
    process_all(json_file, out_dir, passthrough_on_error=True)