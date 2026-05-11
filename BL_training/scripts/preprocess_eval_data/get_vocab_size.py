import json

file_path = "BL_training/data/BL_vocab_OFFICIAL.json"   # change this

with open(file_path, "r") as f:
    data = json.load(f)

print("Number of keys:", len(data.keys()))