# USED FOR MAIN EXPERIMENT (INTRASENT CONDITION)
import os

base = "BL_collection_data/intrasent"

pairs = [
    ("dadcommunity/BL_dadcomm_test_dialogues.txt",
     "dadcommunity/BL_dadcomm_test_outputs.jsonl"),

    ("momcommunity/BL_momcomm_test_dialogues.txt",
     "momcommunity/BL_momcomm_test_outputs.jsonl"),

    ("dadhome/BL_dadhome_test_dialogues.txt",
     "dadhome/BL_dadhome_test_outputs.jsonl"),

    ("momhome/BL_momhome_test_dialogues.txt",
     "momhome/BL_momhome_test_outputs.jsonl"),
]

txt_out = "BL_collection_data/intrasent/intrasent.txt"
jsonl_out = "BL_collection_data/intrasent/intrasent.jsonl"

# --- Combine TXT files ---
with open(txt_out, "w", encoding="utf-8") as fout:
    for txt_rel, _ in pairs:
        path = os.path.join(base, txt_rel)
        with open(path, "r", encoding="utf-8") as fin:
            for line in fin:
                fout.write(line)

# --- Combine JSONL files ---
with open(jsonl_out, "w", encoding="utf-8") as fout:
    for _, json_rel in pairs:
        path = os.path.join(base, json_rel)
        with open(path, "r", encoding="utf-8") as fin:
            for line in fin:
                fout.write(line)

