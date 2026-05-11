#!/bin/bash

# Ensure correct usage
if [[ $# -ne 2 ]]; then
    echo "Usage: bash retrieve_openai_batch_results_continuous.sh <mapping_file> <output_directory>"
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

while IFS=' -> ' read -r file batch_id; do
    if [[ -n "$batch_id" ]]; then
        echo "Checking status of batch: $batch_id (File: $file)"
        
        while true; do
            # Get the batch details (including output_file_id)
            BATCH_DETAILS=$(python3 BL_generation/openai/OpenAI_check_batch_status.py "$batch_id")

            # Extract batch status
            STATUS=$(echo "$BATCH_DETAILS" | grep -oP "status='[^']+" | cut -d"'" -f2)

            # Extract output_file_id if available
            OUTPUT_FILE_ID=$(echo "$BATCH_DETAILS" | grep -oP "output_file_id='file-[^']+" | cut -d"'" -f2)

            echo "Current status: $STATUS"

            if [[ "$STATUS" == "completed" && -n "$OUTPUT_FILE_ID" ]]; then
                echo "Batch completed. Retrieving results..."
                
                # Download and save the results
                python OpenAI_retrieve_batch_output.py "$OUTPUT_FILE_ID" "$OUTPUT_DIR"

                echo "Results for batch $batch_id saved to $OUTPUT_DIR"
                break
            elif [[ "$STATUS" == "failed" ]]; then
                echo "Batch $batch_id failed. Skipping."
                break
            else
                echo "Batch not completed yet. Retrying in 30 seconds..."
                sleep 30  # Wait before checking again
            fi
        done

        echo "-----------------------------------"
    fi
done < "$MAPPING_FILE"

echo "Batch results retrieval completed. Files saved in $OUTPUT_DIR"
