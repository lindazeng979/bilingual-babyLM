import os, sys, json
from tqdm import tqdm

import random
random.seed(0)

def get_vocab(train_file, val_file, out_file):

    # Read files
    with open(train_file, 'r') as f:
        lines = [x.strip() for x in f.readlines()]
    print(len(lines))

    with open(val_file, 'r') as f2:
        lines2 = [x.strip() for x in f2.readlines()]
    print(len(lines2))

    vocab_dict = {}

    # Process train
    for line in tqdm(lines):
        # SIMPLE SPACE SPLIT
        words = line.split()
        for word in words:
            vocab_dict[word] = vocab_dict.get(word, 0) + 1

    # Process val
    for line in tqdm(lines2):
        words = line.split()
        for word in words:
            vocab_dict[word] = vocab_dict.get(word, 0) + 1

    print(len(vocab_dict))

    # Save vocab
    with open(out_file, 'w') as f:
        json.dump(vocab_dict, f, indent=4)


train_file = 'BL_collection_data/all_split_txt_20M/intersent_20M/train.txt'
val_file = 'BL_collection_data/all_split_txt_20M/intersent_20M/val.txt'
out_file = 'BL_training/data/BL_intersent_vocab_20M.json'

get_vocab(train_file, val_file, out_file)