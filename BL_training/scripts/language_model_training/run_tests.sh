#!/bin/bash

set -euo pipefail

BASE_DATA="${BASE_DATA:-/data}"
BASE_TOKENIZERS="${BASE_TOKENIZERS:-/tokenizers}"
BASE_OUT="${BASE_OUT:-/trained_GPT_models}"
CONFIG="tokenizers/GPT2-small_config"

MODEL="${MODEL:-gpt2}"
LR="${LR:-1e-04}"
EPOCHS="${EPOCHS:-20}"
BS="${BS:-4}"

# Examples below
MODELS=(
    GPT2-eng_topline
    GPT2-sp_topline_1
    GPT2-intrasent_0
)

for NAME in "${MODELS[@]}"; do
    CORE_LOG=${NAME#GPT2-}
    CORE=${NAME#GPT2-}      
    SEED=${CORE##*_} 
    TOKENDIR=${CORE%_*}        # removes seed        # 0 or 1
    DATADIR=${TOKENDIR/_80k/}       # intersent_20M

    TRAIN="${BASE_DATA}/${DATADIR}/train.txt"
    VAL="${BASE_DATA}/${DATADIR}/val.txt"
    TOKENIZER="${BASE_TOKENIZERS}/${TOKENDIR}"
    OUTDIR="${BASE_OUT}/${NAME}"
    LOG="${CORE_LOG}.log"

    echo "======================================"
    echo "Running: $NAME"
    echo "  Log:        $LOG"
    echo "  Data dir:   $DATADIR"
    echo "  Token dir:  $TOKENDIR"
    echo "  Seed:       $SEED"
    echo "======================================"

    bash scripts/language_model_training/GPT2_CHILDES_4-GPUs_train.sh \
        "$TRAIN" "$VAL" "$TOKENIZER" "$CONFIG" "$OUTDIR" \
        "$MODEL" "$LR" "$EPOCHS" "$BS" "$SEED" \
        > "$LOG" 2>&1
done