import argparse
import os
import traceback

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, infer_device

device = infer_device()

# ====== DATA PATHS ======
# English
EN_BASE_PATH = "data/eng_topline/val.txt"
EN_20M_PATH = "data/eng_topline_20M/val.txt"

# Spanish
ES_BASE_PATH = "data/sp_topline/val.txt"
ES_20M_PATH = "data/sp_topline_20M/val.txt"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--models",
        nargs="+",
        help="One or more model paths to evaluate.",
    )
    parser.add_argument(
        "--model-dir",
        help="Directory containing model subdirectories to evaluate.",
    )
    parser.add_argument(
        "--out-file",
        default="BL_training/results/perplexity_eval_results.txt",
        help="File to append evaluation results to.",
    )

    return parser.parse_args()


# ───────────────────────────────────────────
# LOAD ALL TEXTS ONCE
# ───────────────────────────────────────────
with open(EN_BASE_PATH, "r", encoding="utf-8") as f:
    en_text_base = f.read()

with open(EN_20M_PATH, "r", encoding="utf-8") as f:
    en_text_20m = f.read()

with open(ES_BASE_PATH, "r", encoding="utf-8") as f:
    es_text_base = f.read()

with open(ES_20M_PATH, "r", encoding="utf-8") as f:
    es_text_20m = f.read()

print("Loaded English BASE char length:", len(en_text_base))
print("Loaded English 20M char length:", len(en_text_20m))
print("Loaded Spanish BASE char length:", len(es_text_base))
print("Loaded Spanish 20M char length:", len(es_text_20m))


# ───────────────────────────────────────────
# PICK TEXT BASED ON MODEL
# ───────────────────────────────────────────
def select_texts_for_model(model_id: str):
    """Return (english_text, spanish_text) based on model suffix."""
    name = os.path.basename(model_id)

    if "20M" in name or "10M" in name:
        print(f"→ {name} detected as 20M/10M → Using ENG_20M + SP_20M")
        return en_text_20m, es_text_20m

    print(f"→ {name} detected as BASE → Using ENG_BASE + SP_BASE")
    return en_text_base, es_text_base


# ───────────────────────────────────────────
# EVALUATION
# ───────────────────────────────────────────
def run_eval_for(model_id):
    print("\n" + "=" * 80)
    print(f"Evaluating model: {model_id}")
    print("=" * 80)

    en_text, es_text = select_texts_for_model(model_id)

    model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    if tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token

    tokenizer.model_max_length = int(1e12)

    max_length = model.config.n_positions
    stride = 512

    def ppl_for_text(text: str) -> float:
        enc = tokenizer(
            text,
            return_tensors="pt",
            truncation=False,
            add_special_tokens=False,
        )
        input_ids = enc.input_ids
        seq_len = input_ids.size(1)

        nll_sum = 0.0
        n_tokens = 0
        prev_end_loc = 0

        for begin_loc in tqdm(range(0, seq_len, stride), desc="Sliding windows"):
            end_loc = min(begin_loc + max_length, seq_len)
            trg_len = end_loc - prev_end_loc

            input_ids_slice = input_ids[:, begin_loc:end_loc].to(device)
            target_ids = input_ids_slice.clone()
            target_ids[:, :-trg_len] = -100

            with torch.no_grad():
                outputs = model(input_ids_slice, labels=target_ids)
                loss = outputs.loss

            num_valid_tokens = (target_ids != -100).sum().item()
            nll_sum += loss.item() * num_valid_tokens
            n_tokens += num_valid_tokens

            prev_end_loc = end_loc
            if end_loc == seq_len:
                break

        avg_nll = nll_sum / max(1, n_tokens)
        return float(torch.exp(torch.tensor(avg_nll)))

    print("→ English perplexity…")
    ppl_en = ppl_for_text(en_text)

    print("→ Spanish perplexity…")
    ppl_es = ppl_for_text(es_text)

    print(f"\nRESULT for {model_id}:")
    print(f"  English PPL: {ppl_en:.2f}")
    print(f"  Spanish PPL: {ppl_es:.2f}")

    return ppl_en, ppl_es


# ───────────────────────────────────────────
# MODEL SELECTION
# ───────────────────────────────────────────
def get_model_ids(args):
    if args.models:
        return args.models

    if args.model_dir:
        model_ids = []
        for name in sorted(os.listdir(args.model_dir)):
            full_path = os.path.join(args.model_dir, name)
            if os.path.isdir(full_path):
                model_ids.append(full_path)
        return model_ids

    raise ValueError("Provide either --models or --model-dir.")


def main():
    args = parse_args()
    model_ids = get_model_ids(args)

    print("\nModels to evaluate:")
    for model_id in model_ids:
        print("  ", model_id)

    results = {}
    for model_id in model_ids:
        try:
            vals = run_eval_for(model_id)
            results[model_id] = vals

            ppl_en, ppl_es = vals
            with open(args.out_file, "a") as f:
                f.write(f"{model_id}: EN={ppl_en:.2f} ES={ppl_es:.2f}\n")

        except Exception as e:
            print("\n" + "!" * 80)
            print(f"ERROR while evaluating model: {model_id}")
            print(f"Exception: {e}")
            traceback.print_exc()

            with open(args.out_file, "a") as f:
                f.write(f"{model_id}: FAILED\n")

            results[model_id] = None


if __name__ == "__main__":
    main()