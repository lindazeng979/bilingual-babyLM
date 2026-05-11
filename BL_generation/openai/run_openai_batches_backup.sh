#!/bin/bash

# Ensure correct usage
if [[ $# -ne 2 ]]; then
    echo "Usage: bash run_openai_batches.sh <input_directory> <output_log_file>"
    exit 1
fi

# Read command-line arguments
INPUT_DIR="$1"
OUTPUT_LOG="$2"

# Ensure the output log is cleared
> "$OUTPUT_LOG"

# Loop through each .jsonl file in the directory
for file in "$INPUT_DIR"/*.jsonl; do
    if [[ -f "$file" ]]; then
        echo "Uploading file: $file"

        # Run OpenAI_upload_batch_file.py and extract the file ID
        FILE_RESPONSE=$(python /scripts/data_collection/openai/OpenAI_upload_batch_file.py "$file")
        FILE_ID=$(echo "$FILE_RESPONSE" | grep -oP "id='file-[^']+" | cut -d"'" -f2)

        if [[ -z "$FILE_ID" ]]; then
            echo "Error: Could not extract file ID for $file"
            continue
        fi

        echo "File uploaded: $file -> File ID: $FILE_ID"

        # Create the batch using the extracted file ID
        BATCH_RESPONSE=$(python BL_generation/openai/OpenAI_create_batch.py "$FILE_ID")
        BATCH_ID=$(echo "$BATCH_RESPONSE" | grep -oP "id='batch-[^']+" | cut -d"'" -f2)

        if [[ -z "$BATCH_ID" ]]; then
            echo "Error: Could not extract batch ID for $file"
            continue
        fi

        echo "Batch created: $file -> Batch ID: $BATCH_ID"

        # Log the mapping for later batch status checking
        echo "$file -> $BATCH_ID" >> "$OUTPUT_LOG"
    fi
done

echo "Batch processing completed. Mapping saved in $OUTPUT_LOG"

#bash run_openai_batches.sh ./input_batches batch_mapping.txt