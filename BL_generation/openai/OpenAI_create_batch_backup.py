import sys
from openai import OpenAI
client = OpenAI()

batch_file_id = sys.argv[1]

batch_input_file_id = batch_file_id
batch = client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
        "description": "TD TEST batch"
    }
)

print(batch)