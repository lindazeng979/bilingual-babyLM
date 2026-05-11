# Input an entire folder of jsons, output into a folder of txts

import json
import os
import sys


# only used for all_experiments, not all_split_exp
def extract_texts_from_file(json_file, txt_file):
    """Extract 'text' fields from a JSON/JSONL file into a TXT file."""
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

def process_directory(in_dir, out_dir="all_txt"):
    os.makedirs(out_dir, exist_ok=True)
    
    for filename in os.listdir(in_dir):
        if filename.endswith(".json") or filename.endswith(".jsonl"):
            json_path = os.path.join(in_dir, filename)
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(out_dir, txt_filename)
            
            print(f"Processing {filename} → {txt_filename}")
            extract_texts_from_file(json_path, txt_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_all.py <json_dir> [out_dir]")
        sys.exit(1)

    in_dir = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "all_txt"
    process_directory(in_dir, out_dir)
    print(f"All texts extracted to {out_dir}/")