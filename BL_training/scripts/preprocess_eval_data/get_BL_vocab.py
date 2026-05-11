import os, sys, json
import nltk
from tqdm import tqdm
nltk.download('punkt')

import random
random.seed(0)


def get_vocab(train_file,val_file,out_file):
    f = open(train_file,'r')
    lines = [x.strip() for x in f.readlines()]#lines = [x.strip() for x in f.readlines() if '**Mom**' not in x] #lines = [x.strip() for x in f.readlines()]
    print(len(lines))
    f2 = open(val_file,'r')
    lines2 = [x.strip() for x in f2.readlines()]  #lines2 = [x.strip() for x in f2.readlines() if '**Mom**' not in x] #flines2 = [x.strip() for x in f2.readlines()]  
    print(len(lines2))
    
    vocab_dict = {}
    for line in tqdm(lines):
        words = nltk.word_tokenize(line)
        for word in words:
            if word not in vocab_dict.keys():
                vocab_dict[word] = 1
            else:
                vocab_dict[word] += 1

    for line in tqdm(lines2):
        words = nltk.word_tokenize(line)
        for word in words:
            if word not in vocab_dict.keys():
                vocab_dict[word] = 1
            else:
                vocab_dict[word] += 1
        
    print(len(list(vocab_dict.keys()))) #23217
    with open(out_file, 'w') as f:
        json.dump(vocab_dict,f,indent=4)
    f.close()


train_file = 'BL_collection_data/all_split_txt_20M/intersent_20M/train.txt'
val_file = 'BL_collection_data/all_split_txt_20M/intersent_20M/val.txt'
out_file = 'BL_training/data/BL_intersent_vocab_20M.json'

get_vocab(train_file,val_file,out_file) #68128 unique words