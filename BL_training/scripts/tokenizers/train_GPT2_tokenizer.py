#! pip install tokenizers

import sys
from transformers import AutoTokenizer
old_tokenizer = AutoTokenizer.from_pretrained("gpt2")

train_path = sys.argv[1] #E.g. 'data/babyLM_github_code_train.txt'
val_path = sys.argv[2] #E.g. 'data/babyLM_github_code_val.txt'
output_path = sys.argv[3] #E.g. 'tokenizers/GPT2_babyLM_github_code'
size = int(sys.argv[4])

#Add <UNK> special token into the vocab
#special_token = '<UNK>'
#old_tokenizer.add_tokens([special_token])
#special_tokens_dict = {'additional_special_tokens': ['<UNK>']}
#old_tokenizer.add_special_tokens(special_tokens_dict)


example = '''def add_numbers(a, b):
    """Add the two numbers `a` and `b`."""
    return a + b'''

tokens = old_tokenizer.tokenize(example)
print(tokens)


def get_training_corpus(raw_dataset):
    return (
        raw_dataset[i : i + 1000]
        for i in range(0, len(raw_dataset), 1000)
    )


paths = [train_path, val_path]

lines = []
for fn in paths:
    f = open(fn,'r')
    lines.extend(f.readlines())
print(len(lines))

token_corpus = get_training_corpus(lines)

new_tok = old_tokenizer.train_new_from_iterator(token_corpus, size)

# --- SPECIAL TOKENS SETUP ---
# Keep EOS as <|endoftext|>; add a proper PAD; don't use UNK for byte-BPE.
specials_to_add = {"pad_token": "<|pad|>"}
num_added = new_tok.add_special_tokens(specials_to_add)

# Ensure IDs are set (bos optional)
new_tok.unk_token = None
# new_tok.bos_token = "<|bos|>"  # uncomment only if you plan to use BOS

# Save tokenizer
new_tok.save_pretrained(output_path)

# Introspection
print("All special tokens:", new_tok.all_special_tokens)
print("Specials map:", new_tok.special_tokens_map)
print("Vocab size (+added):", len(new_tok), f"(+{num_added})")

'''

tokenizer.save_pretrained(output_path)

# Print all special tokens
print("All special tokens:", tokenizer.all_special_tokens)

# Print individual special tokens
print("BOS token:", tokenizer.bos_token)
print("EOS token:", tokenizer.eos_token)
print("PAD token:", tokenizer.pad_token)
print("UNK token:", tokenizer.unk_token)
print("SEP token:", tokenizer.sep_token)
print("CLS token:", tokenizer.cls_token)
print("MASK token:", tokenizer.mask_token)
'''