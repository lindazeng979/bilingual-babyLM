import json
import re
import sys
import os

def preprocess_content(content):
    """Preprocess the content by applying required transformations."""
    content = re.sub(r"^DIALOGUE:\n", "", content)
    content = content.replace("\n\n", " \n\n ")
    return content

def total_word_count(file_path):
    """Return the total word count across all lines in a JSONL file."""
    total_word_count = 0
    line_counter = 0
    
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                data = json.loads(line)
                content = (
                    data.get("response", {})
                        .get("body", {})
                        .get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                )
                cleaned_content = preprocess_content(content)
                line_counter += 1
                total_word_count += len(cleaned_content.split())
            except json.JSONDecodeError:
                continue
    
    return total_word_count, line_counter

def total_word_count_all(root_folder="batch0"):
    """Walk through all /outputs folders under root_folder and sum word counts."""
    grand_total = 0
    grand_lines = 0
    
    for dirpath, dirnames, filenames in os.walk("BL_collection_data/" + root_folder):
        if os.path.basename(dirpath) == "outputs":
            for fname in filenames:
                file_path = os.path.join(dirpath, fname)
                total, n_lines = total_word_count(file_path)
                grand_total += total
                grand_lines += n_lines
                print(f"{file_path}: {total} words across {n_lines} lines")
    
    print("\n=== GRAND TOTAL ===")
    print(f"Total word count across all files: {grand_total}")
    if grand_lines:
        print(f"Average per line (all files): {grand_total / grand_lines:.2f}")
    return grand_total, grand_lines

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "batch0"
    total_word_count_all(root)