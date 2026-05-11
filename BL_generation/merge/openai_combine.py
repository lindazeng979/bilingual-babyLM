import os

# combines diff conditions all into 1 file

base_dir = "BL_collection_data/english"  # your main folder
output_file = base_dir + "/" + "test3_english_test_dialogues_combined.txt"

with open(output_file, "w", encoding="utf-8") as outfile:
    for root, _, files in os.walk(base_dir):
        #print(files)
        for filename in files:
            #print(filename)
            if filename.endswith("_test_dialogues.txt"):
                #print(filename)
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read().strip()
                    outfile.write(content + "\n\n")  # separator between files
                print(f"Added: {file_path}")

print(f"\n✅ Combined all test dialogues into {output_file}")