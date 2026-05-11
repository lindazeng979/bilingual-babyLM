import re

def count_unique_words_old(file1, file2):
    words = set()
    for fname in [file1, file2]:
        with open(fname, "r", encoding="utf-8") as f:
            text = f.read().lower()
            words.update(re.findall(r"\b\w+\b", text))
    return len(words)

from nltk.tokenize import word_tokenize
import nltk
nltk.download("punkt")

def count_unique_words(file1, file2):
    vocab = set()
    for fname in [file1, file2]:
        with open(fname, "r", encoding="utf-8") as f:
            for line in f:
                tokens = word_tokenize(line.lower())
                vocab.update(tokens)
    return len(vocab)


print(count_unique_words("/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/intersent/train.txt",
 "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/intersent/val.txt"))
print(count_unique_words("/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/intrasent/train.txt",
 "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/intrasent/val.txt"))
print(count_unique_words("/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/eng_topline/train.txt",
 "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/eng_topline/val.txt"))
print(count_unique_words("/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/sp_topline/train.txt",
 "/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/sp_topline/val.txt"))