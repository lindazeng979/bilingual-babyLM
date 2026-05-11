#!/bin/bash

# Fill this in if trained_GPT2_models is not in BL_training
# ====== EDIT BASE PATH HERE ======
MODEL_DIR="" 

# Results directory
results_dir="results" # edit if results is not directly in working directory
mkdir -p "${results_dir}"

# -------------------------------
# MODELS TO RUN (edit this)
# -------------------------------
MODEL_NAMES=(
    "trained_GPT2_models/GPT2-eng_topline"
    "trained_GPT2_models/GPT2-sp_topline"
)

echo "Running Zorro eval on selected models in: ${MODEL_DIR}"
echo

# Loop through explicitly listed model names
for model_name in "${MODEL_NAMES[@]}"; do
    ckpt_path="${MODEL_DIR}/${model_name}"

    # Skip if model directory does not exist
    if [ ! -d "${ckpt_path}" ]; then
        echo "⚠️ Skipping ${model_name}: directory not found at ${ckpt_path}"
        echo
        continue
    fi

    echo "Processing model: ${model_name}"

    # ------------------------------
    # Determine which Zorro variant
    # ------------------------------
    if [[ "$model_name" == *20M* || "$model_name" == *10M* ]]; then
        ZORRO_MAIN="zorro_20M"
        ZORRO_MOM="zorro_OFFICIAL_20M_dialogue-format-BL_Mom"
        PREFIX_MAIN="20M"
        PREFIX_MOM="20M_MOM"
    else
        ZORRO_MAIN="zorro_OFFICIAL"
        ZORRO_MOM="zorro_OFFICIAL_dialogue-format-BL_Mom"
        PREFIX_MAIN="100M"
        PREFIX_MOM="100M_MOM"
    fi

    echo " → Using main task: ${ZORRO_MAIN}"
    echo " → Using mom-task:  ${ZORRO_MOM}"

    # ------------------------------
    # Main OFFICIAL evaluation
    # ------------------------------
    python babylm_eval_zorro.py \
        "${ckpt_path}" \
        decoder \
        "${ZORRO_MAIN}" \
        "${results_dir}/${PREFIX_MAIN}_all_exp_results-zorro.txt" \
        "${results_dir}/${PREFIX_MAIN}_all_exp_final_avg-zorro.csv" \
        "${results_dir}/${PREFIX_MAIN}_all_exp_best_layer-zorro.csv" \
        "${results_dir}/${PREFIX_MAIN}_all_exp_results-zorro.jsonl"

    # ------------------------------
    # Dialogue-format Mom evaluation
    # ------------------------------
    python babylm_eval_zorro.py \
        "${ckpt_path}" \
        decoder \
        "${ZORRO_MOM}" \
        "${results_dir}/${PREFIX_MOM}_all_exp_results-zorro.txt" \
        "${results_dir}/${PREFIX_MOM}_all_exp_final_avg-zorro.csv" \
        "${results_dir}/${PREFIX_MOM}_all_exp_best_layer-zorro.csv" \
        "${results_dir}/${PREFIX_MOM}_all_exp_results-zorro.jsonl"

    if [ $? -eq 0 ]; then
        echo "Successfully processed ${model_name}."
    else
        echo "Error processing ${model_name}."
    fi

    echo
done