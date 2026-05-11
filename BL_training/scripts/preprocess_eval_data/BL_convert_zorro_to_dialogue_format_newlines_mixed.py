import os, sys, json, random, itertools
from tqdm import tqdm

random.seed(0)

# ===== CHOOSE MODE =====
# "balanced" → 1/3 Child, 1/3 Mom, 1/3 Dad
# "weighted" → 47% Child, 26.5% Mom, 26.5% Dad
MODE = "weighted"   # change to "weighted" if you want ratios

LABELS = ["Child", "Mom", "Dad"]
WEIGHTS = [0.47, 0.265, 0.265]  # only used if MODE = "weighted"
cycler = itertools.cycle(LABELS)  # for balanced mode

def read_json_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            dictionary = json.loads(line)
            data.append(dictionary)
    return data

def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        for dictionary in data:
            json.dump(dictionary, file)
            file.write('\n')

def convert_examples(in_file):
    input_examples = read_json_file(in_file)
    output_examples = []

    for example in tqdm(input_examples):
        if MODE == "balanced":
            speaker_label = next(cycler)
        else:  # weighted
            speaker_label = random.choices(LABELS, weights=WEIGHTS, k=1)[0]

        sentence1 = example['sentence_good']
        sentence2 = example['sentence_bad']
        sentence1_dialogue = f'\\n\\n **{speaker_label}**: ' + sentence1 + ' \\n\\n'
        sentence2_dialogue = f'\\n\\n **{speaker_label}**: ' + sentence2 + ' \\n\\n'

        example['sentence_good'] = sentence1_dialogue
        example['sentence_bad'] = sentence2_dialogue
        output_examples.append(example)

    suffix = "balanced" if MODE == "balanced" else "weighted"
    out_file = in_file.replace(
        'BL-data_zorro',
        f'BL-data_zorro_dialogue-format-BL_mixed-{suffix}'
    )
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    print("Wrote:", out_file)
    write_json_file(out_file, output_examples)

# ===== RUN =====
in_path = 'evaluation-pipeline/BL-data_zorro'
in_files = [os.path.join(in_path, x) for x in os.listdir(in_path)]

for in_file in in_files:
    print(f"\nProcessing {in_file}")
    convert_examples(in_file)