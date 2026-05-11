import json

def read_json_vocab(path):
    with open(path, 'r') as f:
        return json.load(f)

def write_json_vocab(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def vocab_union(v1, v2, mode="max"):
    """
    mode = "max" or "sum"
    """
    all_words = set(v1.keys()) | set(v2.keys())
    out = {}

    for w in all_words:
        c1 = v1.get(w, 0)
        c2 = v2.get(w, 0)

        if mode == "max":
            out[w] = max(c1, c2)
        elif mode == "sum":
            out[w] = c1 + c2
        else:
            raise ValueError("mode must be 'max' or 'sum'")

    return out

def vocab_intersection(v1, v2, mode="max"):
    """
    mode = "max" or "sum"
    """
    common_words = set(v1.keys()) & set(v2.keys())
    out = {}

    for w in common_words:
        c1 = v1[w]
        c2 = v2[w]

        if mode == "max":
            out[w] = "na"
        elif mode == "sum":
            out[w] = "na"
        else:
            raise ValueError("mode must be 'max' or 'sum'")

    return out

def combine_vocab_files(file1, file2, out_file, operation="union", mode="max"):
    """
    operation = "union" or "intersection"
    mode = "max" or "sum"
    """
    v1 = read_json_vocab(file1)
    v2 = read_json_vocab(file2)

    if operation == "union":
        result = vocab_union(v1, v2, mode=mode)
    elif operation == "intersection":
        result = vocab_intersection(v1, v2, mode=mode)
    else:
        raise ValueError("operation must be 'union' or 'intersection'")

    write_json_vocab(out_file, result)
    print(f"Saved {operation} ({mode}) vocab to {out_file} with {len(result)} entries.")

combine_vocab_files(
    "BL_training/data/BL_intersent_vocab_20M.json",
    "BL_training/data/BL_sp_vocab_20M.json",
    "BL_training/data/BL_vocab_combined_20M.json",
    operation="intersection",
    mode="sum"
)