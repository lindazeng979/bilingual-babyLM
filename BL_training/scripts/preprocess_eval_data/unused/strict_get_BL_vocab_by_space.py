import os, json
from collections import defaultdict
from tqdm import tqdm

# ---- Config ----
input_dir = "BL_collection_data/all_txt_nosplit"
output_dir = "BL_training/data"
os.makedirs(output_dir, exist_ok=True)
out_file = os.path.join(output_dir, "BL_vocab_OFFICIAL_spaces.json")


# ---- Get all .txt files except sp_topline ----
txt_files = sorted([
    f for f in os.listdir(input_dir)
    if f.endswith(".txt") and "sp_topline" not in f
])

if not txt_files:
    raise ValueError(f"No .txt files found in {input_dir} (after filtering).")

doc_freq = defaultdict(int)
total_counts = defaultdict(int)
num_files = len(txt_files)

print(f"Found {num_files} .txt files (excluding sp_topline.txt).")

# ---- Main loop ----
for filename in tqdm(txt_files, desc="Processing files", position=0):
    path = os.path.join(input_dir, filename)
    seen_in_this_file = set()

    # Count total lines to make tqdm accurate
    with open(path, "r") as f:
        total_lines = sum(1 for _ in f)

    with open(path, "r") as f:
        for line in tqdm(f, total=total_lines, desc=f"{filename}", position=1, leave=False):
            words = line.split()
            for word in words:
                seen_in_this_file.add(word)

    for w in seen_in_this_file:
        doc_freq[w] += 1

# ---- Filter intersection ----
common_vocab = {
    w: {"total_count": total_counts[w], "doc_freq": doc_freq[w]}
    for w in doc_freq
    if doc_freq[w] == num_files
}

print(f"Common vocab size (present in ALL {num_files} files): {len(common_vocab)}")

# ---- Save ----
with open(out_file, "w") as f:
    json.dump(common_vocab, f, indent=2)

print(f"Saved common vocabulary to: {out_file}")