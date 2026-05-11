import sys
import json
from openai import OpenAI

client = OpenAI()

# Ensure correct usage
if len(sys.argv) != 2:
    print("Usage: python OpenAI_see_all_batches.py <output_file.jsonl>")
    sys.exit(1)

# Read output file path from the command line
output_file = sys.argv[1]

# Fetch all batches
response = client.batches.list(limit=5)

# Check if there are batches
if not response.data:
    print("No batches found.")
    sys.exit(0)

# Overwrite the file if it exists
with open(output_file, "w", encoding="utf-8") as f:
    for batch in response.data:
        json.dump(batch.dict(), f)  # Convert Batch object to dictionary
        f.write("\n")  # Newline to make it JSONL

print(f"All batches saved to {output_file}")