import sys
from openai import OpenAI
import os

client = OpenAI()

input_file = sys.argv[1]

batch_input_file = client.files.create(
    file=open(input_file, "rb"),
    purpose="batch"
)

print(batch_input_file)