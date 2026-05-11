# Input a single json, output into a single txt

import json
import sys
import os

def extract_text(json_file, txt_file):
    with open(json_file, "r", encoding="utf-8") as f_in, \
         open(txt_file, "w", encoding="utf-8") as f_out:
        
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "text" in obj:
                    # write text as one line
                    f_out.write(obj["text"].replace("\n", " ") + "\n")
            except json.JSONDecodeError:
                # maybe the file is a big JSON array instead of JSONL
                try:
                    data = json.loads(line)
                    if isinstance(data, list):
                        for obj in data:
                            if isinstance(obj, dict) and "text" in obj:
                                f_out.write(obj["text"].replace("\n", " ") + "\n")
                except:
                    continue

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 extract_texts.py <input.json> <output.txt>")
        sys.exit(1)

    json_file = sys.argv[1]
    txt_file = sys.argv[2]

    extract_text(json_file, txt_file)
    print(f"Extracted texts written to {txt_file}")