import os, json, re
from tqdm import tqdm
import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize import word_tokenize

# ---------- helpers ----------
def read_vocab(path):
    with open(path, 'r', encoding='utf-8') as f:
        v = json.load(f)
    if isinstance(v, dict):
        return set(k.lower() for k in v.keys())
    elif isinstance(v, list):
        return set(x.lower() for x in v)
    else:
        raise ValueError("Unsupported vocab format")

ALNUM_RE = re.compile(r"[A-Za-z0-9]")

def tokens_to_check(text):
    return [t.lower() for t in word_tokenize(text) if ALNUM_RE.search(t)]

def jsonl_iter(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def write_jsonl(path, items):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for obj in items:
            json.dump(obj, f, ensure_ascii=False)
            f.write('\n')

# ---------- core filter ----------
def filter_zorro_jsonl(in_file, vocab_set, out_dir):
    kept = []
    total = 0
    total_tok = 0
    unk_tok = 0

    for ex in tqdm(jsonl_iter(in_file), desc=f"Filtering {os.path.basename(in_file)}"):
        total += 1
        sg = ex.get("sentence_good", "")
        sb = ex.get("sentence_bad", "")
        toks = tokens_to_check(sg) + tokens_to_check(sb)

        total_tok += len(toks)
        unknown = [t for t in toks if t not in vocab_set]
        unk_tok += len(unknown)

        if not unknown:
            kept.append(ex)

    frac = (len(kept) / total) if total else 0.0
    unk_frac = (unk_tok / total_tok) if total_tok else 0.0

    print(len(kept))
    print(f"{len(kept)} out of {total} ({frac:.4f}) kept")
    print(f"{unk_tok} out of {total_tok} ({unk_frac:.4f}) tokens unknown")

    # new output path under BL-data_zorro
    fname = os.path.basename(in_file)
    out_file = os.path.join(out_dir, fname)
    write_jsonl(out_file, kept)

# ---------- CONFIG ----------
vocab_file = 'BL_training/data/BL_vocab_OFFICIAL.json'
in_path = 'BL_training/evalution-pipeline/filter-data_zorro'
out_path = 'BL_training/evaluation-pipeline/BL-data_zorro_OFFICIAL'

vocab = read_vocab(vocab_file)
for name in os.listdir(in_path):
    if name.lower().endswith('.json'):
        infile = os.path.join(in_path, name)
        print(f"\n{infile}")
        filter_zorro_jsonl(infile, vocab, out_path)