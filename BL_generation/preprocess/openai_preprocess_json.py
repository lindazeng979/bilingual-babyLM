import json
import random
import os
import sys
import re
from tqdm import tqdm
random.seed(0)

#merge batches within one folder and preprocess

def filter_example(content):
    """Preprocess the content by filtering out invalid examples."""

    if 'DIALOGUE:' not in content:
        print("no dialogue")
        #print(content)
        return True
    
    if content.lower().count('dialogue:') > 1:
        print("double dialogue")
        return True
    
    #if '-year-old' in content.lower():
    #    print("year old")
    #    return True
    
    if '**' not in content:
        print("no bold")
        return True
    
    if len(content.split()) > 500:
        print("over line limit")
        return True

    return False


def preprocess_content(content):
    """Preprocess the content by applying required transformations."""
    
    content = content.strip()
    
    # Remove "DIALOGUE:\n" at the beginning
    #content = re.sub(r"^DIALOGUE:\n\n", "", content)
    #content = re.sub(r"^DIALOGUE:\n", "", content)
    #content = re.sub(r"^DIALOGUE:  \n", "", content)
    #content = re.sub(r"^DIALOGUE:  ", "", content)
    #content = re.sub(r"^DIALOGUE: ", "", content)
    #content = re.sub(r"^DIALOGUE:", "", content)
    #content = content.replace("**DIALOGUE:**", "")
    #content = content.replace("DIALOGUE:", "")
    
    # Remove everything before (and including) the first occurrence of "DIALOGUE:"
    content = re.sub(r"(?s)^.*?DIALOGUE:\s*", "", content)
    
    #content = content.replace(" - ", "")
    
    # Ensure newlines are explicit tokens and not treated as actual newlines
    content = content.replace("\n", "\\n")
    
    # Ensure spaces before and after double newlines (utterance separators)
    content = content.replace("\\n\\n", " \\n\\n ")

    # Get rid of extra newline tokens at beginning of lines
    if content.startswith("\\n"):
        content = content[2:]

    # Ensure all utterance separator tokens are double newline tokens with whitespace before and after
    content = content.replace("\\n'\\n**", ' \\n\\n **').replace('\\n**',' \\n\\n **')
    
        # Fix colon placement: **Label:** → **Label**:
    content = re.sub(r"\*\*([^*]+):\*\*", r"**\1**:", content)
    
    # Replace 'Toddler' speaker label with 'Child' speaker label
    content = content.replace("**Toddler**", "**Child**").replace("**toddler**", "**Child**").replace("**Toddler", "**Child").replace("Toddler**","Child**").replace("Toddler","Child").replace("toddler","child").replace("TODDLER","Child")
    vcontent = content.replace("**Teenager**", "**Child**").replace("**teenager**", "**Child**").replace("**Teenager", "**Child").replace("Teenager**","Child**").replace("Teenager","Child").replace("teenager","child").replace("TEENAGER","Child")
    
    # Replace all "curly/smart" quotes and apostraphes with straight ones:
    content = content.replace("’","'").replace("‘","'").replace("“","\"").replace("”","\"")
    
    # Replace EOS token for GPT-2 training
    content = content.strip() + ' <|endoftext|>'
    
    return content


def combine_jsonl_files(input_files, combined_jsonl_file, txt_file):
    combined_data = []
    combined_dialogues = []
    kept_data_counter = 0
    bad_data_counter = 0
    total_word_count = 0
    
    # Read and combine data from input .jsonl files
    for file_name in tqdm(input_files):
        print(f"Processing {file_name}")
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    data = json.loads(line)  # Parse JSON
                    
                    # Navigate JSON structure to get "content"
                    content = data.get("response", {}).get("body", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # Apply filtering
                    remove_example = filter_example(content)
                    if remove_example:
                        bad_data_counter += 1
                        continue
                        
                    # Apply preprocessing
                    cleaned_content = preprocess_content(content)
                    
                    #Further filter if "dialogue" still in content
                    #if 'dialogue' in cleaned_content.lower():
                    #    print("dialogue")
                    #    bad_data_counter += 1
                    #    continue

                    # Count lines and words
                    kept_data_counter += 1
                    word_count = len(cleaned_content.split())  # Split by whitespace
                    total_word_count += word_count
                    
                    combined_data.append(data)
                    combined_dialogues.append(cleaned_content)
 
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line.strip()}")
                    bad_data_counter += 1
    
    print(f"\n{kept_data_counter} examples kept") 
    print(f"{bad_data_counter} examples skipped")
    print(f"\nTotal word count in dialogues after preprocessing: {total_word_count}")
    print(f"Avg word count per example's dialogue after preprocessing (divide by number of kept examples): {total_word_count / kept_data_counter}")

    assert len(combined_data) == len(combined_dialogues)
    
    random.shuffle(combined_data)
    random.shuffle(combined_dialogues)

    # Write cleaned dialogues to a .txt file
    with open(txt_file, 'w') as file:
        for dialogue in combined_dialogues:
            file.write(dialogue + '\n')
    
    # Write combined data to a new .jsonl file
    with open(combined_jsonl_file, 'w') as file:
        for data in combined_data:
            json.dump(data, file)
            file.write('\n')

    print(len(combined_data))
    print("combined files!")


input_folder = sys.argv[1]
output_jsonl_file = sys.argv[2]
output_txt_file = sys.argv[3]

#print(input_folder)
input_files = [os.path.join(input_folder,file) for file in os.listdir(input_folder)]
print(input_files)
print(f"{len(input_files)} files")
combine_jsonl_files(input_files, output_jsonl_file, output_txt_file)


'''
First 100M collected using OpenAI:

718183 examples kept
1723 examples skipped

Total word count in dialogues after preprocessing: 107106092
Avg word count per example's dialogue after preprocessing (divide by number of kept examples): 149.1368959846722
'''