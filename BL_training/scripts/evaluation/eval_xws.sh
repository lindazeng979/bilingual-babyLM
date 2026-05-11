#!/bin/bash

# Fill this in if trained_GPT2_models is not in BL_training
# ====== EDIT BASE PATH HERE ======
path="" # if this path is edited, uncomment "PREPEND BASE PATH" section

partial_model_paths=(
"trained_GPT2_models/GPT2-baseline_10_random_split_80k_42"
"trained_GPT2_models/GPT2-mini-intrasent_80k_42"
)

# ====== PREPEND BASE PATH ======
#model_paths=()
#for p in "${partial_model_paths[@]}"; do
#    model_paths+=("$path/$p")
#done

# ====== fixed output paths ======
OUT_DIR="results"
OUTPUT_FILE="$OUT_DIR/xws-results.txt"
OUTPUT_CSV="$OUT_DIR/xws-max_layer.csv"
FINAL_AVG_CSV="$OUT_DIR/xws-final_avg.csv"

# --- base (no postfix) ---
EN_WORDS_BASE="SemEval17-Task2/test/subtask1-monolingual/data/en.test.data.OFFICIAL_multilingual.txt"
EN_SCORES_BASE="SemEval17-Task2/test/subtask1-monolingual/keys/en.test.gold.OFFICIAL_multilingual.txt"

ES_WORDS_BASE="SemEval17-Task2/test/subtask1-monolingual/data/es.test.data.OFFICIAL_multilingual.txt"
ES_SCORES_BASE="SemEval17-Task2/test/subtask1-monolingual/keys/es.test.gold.OFFICIAL_multilingual.txt"

CROSS_WORDS_BASE="SemEval17-Task2/test/subtask2-crosslingual/data/en-es.test.data.OFFICIAL_multilingual.txt"
CROSS_SCORES_BASE="SemEval17-Task2/test/subtask2-crosslingual/keys/en-es.test.gold.OFFICIAL_multilingual.txt"

# --- 20M versions (used for both 20M and 10M models) ---
EN_WORDS_20M="SemEval17-Task2/test/subtask1-monolingual/data/en.test.data.OFFICIAL_multilingual_20M.txt"
EN_SCORES_20M="SemEval17-Task2/test/subtask1-monolingual/keys/en.test.gold.OFFICIAL_multilingual_20M.txt"

ES_WORDS_20M="SemEval17-Task2/test/subtask1-monolingual/data/es.test.data.OFFICIAL_multilingual_20M.txt"
ES_SCORES_20M="SemEval17-Task2/test/subtask1-monolingual/keys/es.test.gold.OFFICIAL_multilingual_20M.txt"

CROSS_WORDS_20M="SemEval17-Task2/test/subtask2-crosslingual/data/en-es.test.data.OFFICIAL_multilingual_20M.txt"
CROSS_SCORES_20M="SemEval17-Task2/test/subtask2-crosslingual/keys/en-es.test.gold.OFFICIAL_multilingual_20M.txt"


echo "Running multilingual word-sim eval on models in: ${MODEL_DIR}"
echo "Results will be written to:"
echo "  $OUTPUT_FILE"
echo "  $OUTPUT_CSV"
echo "  $FINAL_AVG_CSV"
echo

for ckpt in "${model_paths[@]}"; do
  echo "==========================="
  echo "Running model: $ckpt"
  echo "==========================="

  model_name=$(basename "$ckpt")

  # choose dataset variant based on model postfix
  if [[ "$model_name" == *20M* || "$model_name" == *10M* ]]; then
    EN_WORDS="$EN_WORDS_20M"
    EN_SCORES="$EN_SCORES_20M"
    ES_WORDS="$ES_WORDS_20M"
    ES_SCORES="$ES_SCORES_20M"
    CROSS_WORDS="$CROSS_WORDS_20M"
    CROSS_SCORES="$CROSS_SCORES_20M"
    echo "Model $model_name detected as 20M/10M → using *_OFFICIAL_multilingual_20M files."
  else
    EN_WORDS="$EN_WORDS_BASE"
    EN_SCORES="$EN_SCORES_BASE"
    ES_WORDS="$ES_WORDS_BASE"
    ES_SCORES="$ES_SCORES_BASE"
    CROSS_WORDS="$CROSS_WORDS_BASE"
    CROSS_SCORES="$CROSS_SCORES_BASE"
    echo "Model $model_name detected as non-20M → using standard *_OFFICIAL_multilingual files."
  fi

  echo "==========================="
  echo "Running model: $ckpt"
  echo "==========================="

  # --- English test ---
  python3 BL_multiling_eval_word_sim.py \
    --ckpt_path "$ckpt" \
    --output_file "$OUTPUT_FILE" \
    --output_csv "$OUTPUT_CSV" \
    --output_final_avg_score_csv "$FINAL_AVG_CSV" \
    --word_pairs_file "$EN_WORDS" \
    --human_scores_file "$EN_SCORES" \
    --dataset_name en_test \
    --overwrite

  # --- Spanish test ---
  python3 BL_multiling_eval_word_sim.py \
    --ckpt_path "$ckpt" \
    --output_file "$OUTPUT_FILE" \
    --output_csv "$OUTPUT_CSV" \
    --output_final_avg_score_csv "$FINAL_AVG_CSV" \
    --word_pairs_file "$ES_WORDS" \
    --human_scores_file "$ES_SCORES" \
    --dataset_name es_test \
    --overwrite

  # --- Cross-lingual test ---
  python3 BL_multiling_eval_word_sim.py \
    --ckpt_path "$ckpt" \
    --output_file "$OUTPUT_FILE" \
    --output_csv "$OUTPUT_CSV" \
    --output_final_avg_score_csv "$FINAL_AVG_CSV" \
    --word_pairs_file "$CROSS_WORDS" \
    --human_scores_file "$CROSS_SCORES" \
    --dataset_name en-es_test \
    --overwrite

  if [[ $? -eq 0 ]]; then
    echo "Finished all tests for $model_name"
  else
    echo "Error encountered while processing $model_name (continuing to next model)"
  fi

  echo
done
