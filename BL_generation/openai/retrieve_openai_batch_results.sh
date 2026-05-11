#!/bin/bash

# Ensure correct usage
if [[ $# -ne 2 ]]; then
    echo "Usage: bash retrieve_openai_batch_results.sh <mapping_file> <output_directory>"
    exit 1
fi

# Read command-line arguments
MAPPING_FILE="$1"
OUTPUT_DIR="$2"/outputs

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

if [[ ! -f "$MAPPING_FILE" ]]; then
    echo "Error: Mapping file '$MAPPING_FILE' not found!"
    exit 1
fi

echo "Retrieving batch results and saving to $OUTPUT_DIR..."

#while IFS='->' read -r file batch_id; do
while read -r line; do
    file="${line%% -> *}"
    batch_id="${line##*-> }"

    if [[ -n "$batch_id" ]]; then
        echo "Fetching batch details for: $batch_id (File: $file)"
        
        # Get the batch details (including output_file_id)
        BATCH_DETAILS=$(python BL_generation/openai/OpenAI_check_batch_status.py "$batch_id")
        
        echo $BATCH_DETAILS
        # Extract output_file_id from response
        OUTPUT_FILE_ID=$(echo "$BATCH_DETAILS" | sed -n "s/.*output_file_id='\(file-[^']*\)'.*/\1/p") #OUTPUT_FILE_ID=$(echo "$BATCH_DETAILS" | grep -oP "output_file_id='file-[^']+" | cut -d"'" -f2)

        if [[ -z "$OUTPUT_FILE_ID" ]]; then
            echo "Warning: No output file found for batch $batch_id. It may not be completed yet."
            continue
        fi

        echo "Retrieving results for batch: $batch_id (Output File ID: $OUTPUT_FILE_ID)"
        
        # Download and save the results to the specified directory
        python BL_generation/openai/OpenAI_retrieve_batch_output.py "$OUTPUT_FILE_ID" "$OUTPUT_DIR"

        echo "-----------------------------------"
    fi
done < "$MAPPING_FILE"

echo "Batch results retrieval completed. Files saved in $OUTPUT_DIR"
