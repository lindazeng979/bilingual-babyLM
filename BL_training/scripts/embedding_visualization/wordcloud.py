#!/usr/bin/env python3
"""
UMAP visualization of token embedding space colored by empirical token language usage
estimated from the English-only and Spanish-only plain-text corpora.

Usage:
pip install torch transformers umap-learn plotly
python3 BL_training/scripts/embedding_visualization/wordcloud.py \
  --model_path BL_training/trained_GPT2_models/GPT2_intrasent \
  --en_txt BL_training/data/eng_topline/train.txt \
  --es_txt BL_training/data/sp_topline/train.txt \
  --out_html BL_training/results/embedding/intrasent_wordcloud.html \
  --max_lines 200000 \
  --min_count 1 \
  --conf_thresh 0.75 \
  --max_tokens 20000 --keep_space_tokens

Then open the saved HTML in browser.
"""


import argparse
from collections import Counter
from typing import Dict, Tuple, Optional

import numpy as np
import umap.umap_ as umap
import plotly.express as px
from transformers import AutoTokenizer, AutoModel


# Paper-friendly, consistent colors
COLOR_MAP = {
    "English": "#1f77b4",  # blue
    "Spanish": "#d62728",  # red
    "Shared":  "#9467bd",  # purple (overlap)
    "Unknown": "#7f7f7f",  # gray (rare/insufficient evidence)
}


SYMBOL_MAP = {
    "English": "circle",
    "Spanish": "diamond",
    "Shared":  "star",
}

def stream_token_counts(tokenizer, txt_path: str, max_lines: Optional[int], max_chars: int = 2000) -> Counter:
    """
    Count token IDs from a plain-text file line-by-line.
    max_chars prevents extremely long lines from dominating runtime.
    """
    counts = Counter()
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break
            line = line.strip()
            if not line:
                continue
            if len(line) > max_chars:
                line = line[:max_chars]
            ids = tokenizer.encode(line, add_special_tokens=False)
            counts.update(ids)
    return counts


def build_token_lang_map(
    tokenizer,
    en_txt: str,
    es_txt: str,
    max_lines: Optional[int],
    min_count: int,
    conf_thresh: float,
) -> Tuple[Dict[int, str], Dict[int, float], Dict[int, float]]:
    """
    Build empirical language labels for each token id.

    Returns:
      label_by_id: token_id -> {"English","Spanish","Shared","Unknown"}
      p_en_by_id:  token_id -> P(EN|token) (0..1)
      p_es_by_id:  token_id -> P(ES|token) (0..1)
    """
    print(f"[Counts] Reading corpora:")
    print(f"  EN: {en_txt}")
    print(f"  ES: {es_txt}")
    en_counts = stream_token_counts(tokenizer, en_txt, max_lines=max_lines)
    es_counts = stream_token_counts(tokenizer, es_txt, max_lines=max_lines)

    label_by_id: Dict[int, str] = {}
    p_en_by_id: Dict[int, float] = {}
    p_es_by_id: Dict[int, float] = {}

    all_ids = set(en_counts.keys()) | set(es_counts.keys())
    for tid in all_ids:
        en = en_counts.get(tid, 0)
        es = es_counts.get(tid, 0)
        total = en + es

        if total == 0:
            label_by_id[tid] = "Unknown"
            p_en_by_id[tid] = 0.0
            p_es_by_id[tid] = 0.0
            continue

        p_en = en / total
        p_es = es / total
        p_en_by_id[tid] = p_en
        p_es_by_id[tid] = p_es

        # Not enough evidence -> Unknown
        if total < min_count:
            label_by_id[tid] = "Unknown"
            continue

        # Dominant language -> English/Spanish; otherwise Shared
        if p_en >= conf_thresh:
            label_by_id[tid] = "English"
        elif p_es >= conf_thresh:
            label_by_id[tid] = "Spanish"
        else:
            label_by_id[tid] = "Shared"

    # Quick stats
    from collections import Counter as C2
    print("[Counts] Label distribution (over token IDs observed in corpora):")
    print(C2(label_by_id.values()))

    return label_by_id, p_en_by_id, p_es_by_id


def is_reasonable_token(t: str) -> bool:
    """Filter out empty/weird tokens. Keep it conservative."""
    if t is None:
        return False
    if not t.strip():
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_path", required=True, help="Path to HF model checkpoint directory")
    ap.add_argument("--en_txt", required=True, help="English-only plain text corpus path")
    ap.add_argument("--es_txt", required=True, help="Spanish-only plain text corpus path")
    ap.add_argument("--out_html", required=True, help="Output HTML path for plot")
    ap.add_argument("--max_lines", type=int, default=200000, help="Lines per corpus to scan (speed/quality tradeoff)")
    ap.add_argument("--min_count", type=int, default=50, help="Min total count per token to label (else Unknown)")
    ap.add_argument("--conf_thresh", type=float, default=0.85, help="Dominance threshold for EN/ES label; else Shared")
    ap.add_argument("--max_tokens", type=int, default=20000, help="Max number of vocab tokens to plot (speed)")
    ap.add_argument(
        "--keep_space_tokens",
        action="store_true",
        help="Keep tokens that start with 'Ġ' (GPT-2 space marker). Default filters them out.",
    )
    ap.add_argument("--seed", type=int, default=0, help="UMAP random seed")
    args = ap.parse_args()

    # Load tokenizer + model
    tok = AutoTokenizer.from_pretrained(args.model_path)
    model = AutoModel.from_pretrained(args.model_path)
    model.eval()

    # Build empirical language labels from corpora
    label_by_id, p_en_by_id, p_es_by_id = build_token_lang_map(
        tok,
        args.en_txt,
        args.es_txt,
        max_lines=args.max_lines,
        min_count=args.min_count,
        conf_thresh=args.conf_thresh,
    )

    # Get embedding matrix
    emb = model.get_input_embeddings().weight.detach().cpu().numpy()  # [V, d]
    vocab_size = emb.shape[0]
    tokens = [tok.convert_ids_to_tokens(i) for i in range(vocab_size)]

    # Select tokens to plot
    keep_ids = []
    for i, t in enumerate(tokens):
        if not is_reasonable_token(t):
            continue
        if (not args.keep_space_tokens) and t.startswith("Ġ"):
            continue
        keep_ids.append(i)
        if len(keep_ids) >= args.max_tokens:
            break

    emb_small = emb[keep_ids]
    vocab_small = [tokens[i] for i in keep_ids]

    # Colors (categorical)
    labels = [label_by_id.get(i, "Unknown") for i in keep_ids]
    p_es = [p_es_by_id.get(i, 0.0) for i in keep_ids]
    p_en = [p_en_by_id.get(i, 0.0) for i in keep_ids]

    # ---- Drop Unknown tokens (no gray points) ----
    keep2 = [j for j, lab in enumerate(labels) if lab != "Unknown"]

    emb_small = emb_small[keep2]
    vocab_small = [vocab_small[j] for j in keep2]
    labels = [labels[j] for j in keep2]
    p_en = [p_en[j] for j in keep2]
    p_es = [p_es[j] for j in keep2]

    print(f"[Plot] After filtering Unknown: {len(labels)} tokens")

    #print(f"[Plot] Using {len(keep_ids)} tokens (max_tokens={args.max_tokens}).")
    print(f"[Plot] Embedding shape: {emb_small.shape}")

    # UMAP projection
    reducer = umap.UMAP(
        n_neighbors=30,
        min_dist=0.1,
        metric="cosine",
        random_state=args.seed,
    )
    u = reducer.fit_transform(emb_small)

    # Build dataframe-ish dict for plotly (lets us show probs on hover)
    hover_data = {
        "token": vocab_small,
        "label": labels,
        "P(EN|tok)": np.round(np.array(p_en), 3),
        "P(ES|tok)": np.round(np.array(p_es), 3),
    }

    # Plot
    fig = px.scatter(
        x=u[:, 0],
        y=u[:, 1],
        color=labels,
        symbol=labels,
        color_discrete_map=COLOR_MAP,
        symbol_map=SYMBOL_MAP,
        category_orders={
            "color": ["English", "Spanish", "Shared"],
            "symbol": ["English", "Spanish", "Shared"],
        },
        hover_name=vocab_small,
        hover_data=hover_data,
        title="Token Embedding Space (UMAP Projection) — Empirical EN/ES/Shared Labels",
    )

    # Marker aesthetics (paper-friendly)
    fig.update_traces(marker=dict(size=4, opacity=0.70, line=dict(width=0)))

    # Layout / axes (UMAP dims have no intrinsic meaning)
    fig.update_layout(
        template="simple_white",
        xaxis_title="UMAP Dimension 1",
        yaxis_title="UMAP Dimension 2",
        font=dict(size=14),
        legend_title_text="Token label",
        margin=dict(l=30, r=30, t=60, b=30),
    )

    # Hide tick labels (optional; usually better for papers)
    fig.update_xaxes(showticklabels=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, zeroline=False)

    fig.write_html(args.out_html, include_plotlyjs="cdn")
    print(f"[Done] Saved HTML to: {args.out_html}")

    # Distribution summary for sanity
    from collections import Counter as C2
    print("[Done] Plot label distribution (in plotted subset):")
    print(C2(labels))


if __name__ == "__main__":
    main()
