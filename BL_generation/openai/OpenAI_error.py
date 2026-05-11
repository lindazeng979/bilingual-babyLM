from openai import OpenAI

client = OpenAI()

# Download error file content
resp = client.files.content("file-THyByKK9UK8aTvd8ZurGxW")

# Save to disk
with open("batch_errors.jsonl", "wb") as f:
    f.write(resp.read())