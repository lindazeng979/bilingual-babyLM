import sys
import os
from openai import OpenAI

client = OpenAI()


# Ensure correct usage
if len(sys.argv) != 3:
    print("Usage: python OpenAI_retrieve_batch_output.py <output_file_id> <output_directory>")
    sys.exit(1)

# Read arguments
output_file_id = sys.argv[1]
output_dir = sys.argv[2]

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define output file path inside the directory
output_filepath = os.path.join(output_dir, f"{output_file_id}.jsonl")

# Retrieve the file content
file_response = client.files.content(output_file_id)

# Save content to the specified directory
with open(output_filepath, "w", encoding="utf-8") as output_file:
    output_file.write(file_response.text)

print(f"Batch results saved to {output_filepath}")
