from openai import OpenAI
client = OpenAI()

batches = client.batches.list(limit=5)

for batch in batches:
    print(batch)