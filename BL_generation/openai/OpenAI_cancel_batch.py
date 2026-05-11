import sys
from openai import OpenAI
client = OpenAI()

batch_ID = sys.argv[1]

client.batches.cancel(batch_ID)