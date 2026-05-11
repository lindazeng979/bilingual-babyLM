#!/bin/bash

# Ensure correct usage
if [[ $# -ne 2 ]]; then
    echo "Usage: bash run_openai_batches.sh <input_directory> <output_log_file>"
    exit 1
fi

# Read command-line arguments
INPUT_DIR="$1"/inputs
OUTPUT_LOG="$2"

# Make sure the parent directory of the log file exists
mkdir -p "$(dirname "$OUTPUT_LOG")"

# Ensure the output log is cleared
> "$OUTPUT_LOG"

# Loop through each .jsonl file in the directory
for file in "$INPUT_DIR"/*.jsonl; do
    if [[ -f "$file" ]]; then
        echo "Uploading file: $file"

        # Run OpenAI_upload_batch_file.py and extract the file ID
        FILE_RESPONSE=$(python BL_generation/openai/OpenAI_upload_batch_file.py "$file")
        FILE_ID=$(echo "$FILE_RESPONSE" | sed -n "s/.*id='\(file-[^']*\)'.*/\1/p") #replaced FILE_ID=$(echo "$FILE_RESPONSE" | grep -oP "id='file-[^']+" | cut -d"'" -f2)

        if [[ -z "$FILE_ID" ]]; then
            echo "Error: Could not extract file ID for $file"
            echo "Raw File Response: $FILE_RESPONSE"
            continue
        fi

        echo "File uploaded: $file -> File ID: $FILE_ID"

        # Create the batch using the extracted file ID and input filename
        BATCH_RESPONSE=$(python BL_generation/openai/OpenAI_create_batch.py "$FILE_ID" "$file")

        # Debugging: Print the raw batch response
        echo "Raw Batch Response: $BATCH_RESPONSE"

        # Extract batch ID
        BATCH_ID=$(echo "$BATCH_RESPONSE" | sed -n "s/.*id='\(batch_[^']*\)'.*/\1/p") # replaced BATCH_ID=$(echo "$BATCH_RESPONSE" | grep -oP "id='batch-[^']+" | cut -d"'" -f2)
		#BATCH_ID=$(echo "$BATCH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

        if [[ -z "$BATCH_ID" ]]; then
            echo "Error: Could not extract batch ID for $file"
			echo "Batch created for $file"
            continue
        fi

        echo "Batch created: $file -> Batch ID: $BATCH_ID"

        # Log the mapping for later batch status checking
        echo "$file -> $BATCH_ID" >> "$OUTPUT_LOG"
    fi
done

echo "Batch processing completed. Mapping saved in $OUTPUT_LOG"
