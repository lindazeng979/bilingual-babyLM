import os, sys, json
import csv
from tqdm import tqdm
import random

random.seed(0)

def read_dict_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # strip newline and whitespace, but keep alignment (no empty lines)
        lines = [line.rstrip('\n') for line in lines]
    return lines


def write_txt_file(file_path, lines):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(f"{line}\n")


def filter_examples_txt_and_gold(data_file, gold_file, vocab_dict):
    # data_file: lines like "word1\tword2"
    input_examples = read_txt_file(data_file)
    gold_lines = read_txt_file(gold_file)

    if len(input_examples) != len(gold_lines):
        print(f"WARNING: data and gold have different lengths: "
              f"{len(input_examples)} vs {len(gold_lines)}")
        # You can choose to assert here if you want strict behavior:
        # assert False, "Data and gold file lengths do not match."

    original_len = len(input_examples)
    kept_examples = []
    kept_gold = []
    total_word_count = 0
    unknown_word_count = 0

    for ex_line, gold_line in tqdm(
        list(zip(input_examples, gold_lines)),
        total=original_len
    ):
        line = ex_line.strip()

        # skip comments / empty lines in both files
        if not line or line.startswith('#'):
            continue

        parts = line.split('\t')
        if len(parts) < 2:
            # malformed: skip both data and gold
            continue

        word1, word2 = parts[0].strip(), parts[1].strip()

        include_example = True
        total_word_count += 2

        for word in [word1, word2]:
            if word not in vocab_dict:
                include_example = False
                unknown_word_count += 1

        if include_example:
            # keep the original format in data
            kept_examples.append(f"{word1}\t{word2}")
            # keep the aligned gold label line as-is
            kept_gold.append(gold_line)

    print(len(kept_examples))
    print(f"{len(kept_examples)} out of {original_len} "
          f"({len(kept_examples)/original_len if original_len else 0:.4f} fraction) kept")
    print(f"{unknown_word_count} out of {total_word_count} "
          f"({unknown_word_count/total_word_count if total_word_count else 0:.4f} fraction) words unknown")

    # Construct output paths
    # e.g. es.test.data.txt -> es.test.data.OFFICIAL_multilingual_20M.txt
    out_data_file = data_file.replace(
        'test.data',
        'test.data.OFFICIAL_multilingual_20M'
    )
    # e.g. es.test.gold.txt -> es.test.gold.OFFICIAL_multilingual_20M.txt
    out_gold_file = gold_file.replace(
        'test.gold',
        'test.gold.OFFICIAL_multilingual_20M'
    )

    write_txt_file(out_data_file, kept_examples)
    write_txt_file(out_gold_file, kept_gold)


# vocab_file = '/Users/lindazeng/Documents/bilingual-llms/BL_training/data/BL_vocab.json'
vocab_file = 'BL_training/data/BL_vocab_OFFICIAL_multilingual_20M.json'
vocab_dict = read_dict_file(vocab_file)

data_file = "BL_training/SemEval17-Task2/test/subtask2-crosslingual/data/en-es.test.data.txt"
gold_file = "BL_training/SemEval17-Task2/test/subtask2-crosslingual/keys/en-es.test.gold.txt"

print(f"\nFiltering {data_file} with aligned gold {gold_file}")
filter_examples_txt_and_gold(data_file, gold_file, vocab_dict)