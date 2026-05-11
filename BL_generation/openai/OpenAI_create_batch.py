import sys
import json
import os
from openai import OpenAI

client = OpenAI()

# Ensure correct usage
if len(sys.argv) != 3:
    print("Usage: python OpenAI_create_batch.py <batch_file_id> <original_filename>")
    sys.exit(1)

batch_file_id = sys.argv[1]
original_filename = os.path.basename(sys.argv[2])  # Extracts filename only

try:
    batch = client.batches.create(
        input_file_id=batch_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": original_filename}  # Use filename as description
    )

    # Convert batch to dict explicitly
    #print(batch)
    #batch_dict = dict(batch)

    print(batch)
    #print(json.dumps(batch_json, indent=2))  # Print full response as JSON
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
