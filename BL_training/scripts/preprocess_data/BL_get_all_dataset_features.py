import re

def get_total_words():
    return 1

def get_total_tokens():
    return 1

def get_average_sentence_length():
    return 1

def count_unique_words(file1, file2):
    words = set()
    for fname in [file1, file2]:
        with open(fname, "r", encoding="utf-8") as f:
            text = f.read().lower()
            words.update(re.findall(r"\b\w+\b", text))
    return len(words)