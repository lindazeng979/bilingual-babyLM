import sys
import json
from openai import OpenAI

client = OpenAI()

# Ensure correct usage
if len(sys.argv) != 2:
    print("Usage: python OpenAI_see_all_batches_json.py <output_file.jsonl>")
    sys.exit(1)

# Read output file path from the command line
output_file = sys.argv[1]

# Set limit per request
LIMIT = 10  # Adjust based on API performance
after = None  # Used for pagination

# Overwrite the output file
with open(output_file, "w", encoding="utf-8") as f:
    while True:
        # Fetch batches (use 'after' for pagination)
        if after:
            response = client.batches.list(limit=LIMIT, after=after)
        else:
            response = client.batches.list(limit=LIMIT)

        # If no more batches, stop
        if not response.data:
            break

        # Write each batch to JSONL file
        for batch in response.data:
            json.dump(batch.model_dump(), f)  # Convert batch object to dictionary (Pydantic v2 fix)
            f.write("\n")  # Newline for JSONL format

        # Update 'after' with the last batch ID to fetch next page
        after = response.data[-1].id if len(response.data) == LIMIT else None

        # If there are no more pages, break the loop
        if not after:
            break

print(f"All batches saved to {output_file}")
