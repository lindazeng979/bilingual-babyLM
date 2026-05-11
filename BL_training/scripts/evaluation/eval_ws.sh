#!/bin/bash

# Fill this in if trained_GPT2_models is not in BL_training
CKPT_ROOT="${CKPT_ROOT:?}"

# List of model names for the first set
model_names=(
    "trained_GPT2_models/GPT2-eng_topline"
    "trained_GPT2_models/GPT2-sp_topline"
)

for model_name in "${model_names[@]}"; do
    ckpt_path="${CKPT_ROOT}/${model_name}"

    # Determine eval_dir based on model name
    if [[ "$model_name" == *20M* || "$model_name" == *10M* ]]; then
        EVAL_DIR="data/OFFICIAL_20M"
    else
        EVAL_DIR="data/OFFICIAL"
    fi

    echo "Processing ${model_name}"
    echo "  -> Eval directory: ${EVAL_DIR}"

    python eval_word_sim.py \
        --ckpt_path "${ckpt_path}" \
        --output_file /results/persian_all_exp_results-wr.txt \
        --output_csv //results/persian_all_exp_best_layer-wr.csv \
        --output_final_avg_score_csv /results/persian_all_exp_final_avg-wr.csv \
        --eval_dir "${EVAL_DIR}" \
        --overwrite

    if [ $? -eq 0 ]; then
        echo "Successfully processed ${model_name}"
    else
        echo "Error processing ${model_name}"
    fi

    echo
done