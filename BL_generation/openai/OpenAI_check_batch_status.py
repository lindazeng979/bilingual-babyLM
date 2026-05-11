import sys
from openai import OpenAI
client = OpenAI()

batch_ID = sys.argv[1]

batch = client.batches.retrieve(batch_ID)
print(batch)