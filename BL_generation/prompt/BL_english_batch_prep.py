import sys
import json
import os
from tqdm import tqdm
import random
import csv
#random.seed(0)
from utils import (
    WORD_BANK_NOUNS, WORD_BANK_VERBS,
    AOA_NOUNS, AOA_VERBS
)

model_deployment_name = sys.argv[1]
turn = int(sys.argv[2])
amount = int(sys.argv[3])
part = sys.argv[4]
parent = sys.argv[5].lower()       # mom or dad
setting = sys.argv[6].lower()     # home or community

if parent not in ['mom', 'dad']:
    sys.exit("Parent must be 'mom' or 'dad'")
if setting not in ['home', 'community']:
    sys.exit("Setting must be 'home' or 'community'")
if turn not in [5, 10]:
    sys.exit("Invalid number of turns")

def _label_for_setting(setting: str) -> str:
    """Map 'home'/'community' to mapping labels ('home'/'public')."""
    setting = (setting or "").strip().lower()
    if setting not in {"home", "community"}:
        raise ValueError("setting must be 'home' or 'community'")
    return "public" if setting == "community" else "home"

def load_wordbank(wordbank_file: str, setting: str):
    """
    Load words from WordBank and return (verbs, nouns, adjectives),
    filtered by 'home' vs 'community' using category mappings.
    """
    label = _label_for_setting(setting)

    # Build lowercase sets for fast membership checks
    noun_categories = {k.lower() for k, v in WORD_BANK_NOUNS.items() if v == label}
    verb_categories = {k.lower() for k, v in WORD_BANK_VERBS.items() if v == label}
    #adj_categories  = {k.lower() for k, v in WORD_BANK_ADJS.items()  if v == label}

    verbs, nouns, adjectives = [], [], []

    with open(wordbank_file, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)  # skip header
        for row in csvreader:
            if not row or len(row) < 4:
                continue
            word = row[2].strip()
            category_fallback = row[3].strip().lower()
            category_raw = row[20].strip()
            category = category_raw.lower()

            if category in verb_categories:
                verbs.append(word)
            elif category in noun_categories:
                nouns.append(word)
            else:
                if category_fallback == "descriptive_words":
                    adjectives.append(word)

    return verbs, nouns, adjectives


def load_aoa(AoA_file: str, setting: str):
    """
    Load words from AoA norms (≤ age 10) and return (verbs, nouns, adjectives),
    filtered by 'home' vs 'community' using category mappings.
    """
    label = _label_for_setting(setting)

    # Build lowercase sets for fast membership checks
    noun_categories = {k.lower() for k, v in AOA_NOUNS.items() if v == label}
    verb_categories = {k.lower() for k, v in AOA_VERBS.items() if v == label}
    #adj_categories  = {k.lower() for k, v in AOA_ADJS.items()  if v == label}

    verbs, nouns, adjectives = [], [], []

    with open(AoA_file, newline='', encoding='ISO-8859-1') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)  # skip header
        for row in csvreader:
            if not row or len(row) < 17:
                continue
            word = row[0].strip()
            POS = row[3].strip()
            AoA_Kup = row[8].strip()
            category_raw = row[16].strip()
            category = category_raw.lower()

            # Age filter: keep only AoA <= 10
            try:
                if (not AoA_Kup) or (AoA_Kup.upper() == 'NA') or (float(AoA_Kup) > 10):
                    continue
            except ValueError:
                continue

            if POS == 'Verb' and category in verb_categories:
                verbs.append(word)
            elif POS == 'Noun' and category in noun_categories:
                nouns.append(word)
            elif POS == 'Adjective':
                adjectives.append(word)

    return verbs, nouns, adjectives

wordbank_file = '/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/wordbank_CDI_vocab/OFFICIAL-wordbank_aligned_with_fallback_WordNet.csv'
AoA_file = '/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/AoA_norms/OFFICIAL-AoA_all_with_midlevel.csv'

wb_verbs, wb_nouns, wb_adjs = load_wordbank(wordbank_file, setting)
aoa_verbs, aoa_nouns, aoa_adjs = load_aoa(AoA_file, setting)

print(f'Wordbank: {len(wb_verbs)} verbs, {len(wb_nouns)} nouns, {len(wb_adjs)} adjectives')
print(f'AoA: {len(aoa_verbs)} verbs, {len(aoa_nouns)} nouns, {len(aoa_adjs)} adjectives')

print(wb_verbs[:5], '...', wb_verbs[-5:])
print(aoa_nouns[:5], '...', aoa_nouns[-5:])

#example_output_file = f'TD_collection_data/age-2/TD_age-2_{turn}-turns_{amount}-ex_{part}_examples_openai.jsonl'
#batch_output_file = f'TD_collection_data/age-2/TD_age-2_{turn}-turns_{amount}-ex_{part}_batch_openai.jsonl'

type_lst = [
    'explanatory. It should involve explaining something(s) and potentially answering question(s).',
    'functional. It should involve attempting to get something(s) done or accomplishing particular goal(s).',
    'narrative. It should involve telling a story (real or fictional) or sharing/recounting an experience.',
    'argumentative. It should involve conflict(s) or disagreement(s) that lead to an argument. In most cases, the argument should be resolved, resulting in the child learning.'
]

age_list = [2, 5, 10, 15]  # All allowed ages
#participant_num_lst = [1, 2] if turn in [5, 10] else sys.exit("Invalid number of turns")
#extra_participant_lst = ['older sibling', 'babysitter', 'teacher', 'friend']
#home_examples = ['kitchen', 'living room', 'backyard', 'bedroom', 'garage']
#community_examples = ['school','supermarket', 'school playground', 'library', 'park', 'community center']

# Output files & directories
parent_setting = f"{parent}{setting}"
output_dir = f'BL_collection_data/english/{parent_setting}'
metadata_dir = f'{output_dir}/metadata'
inputs_dir = f'{output_dir}/inputs'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(metadata_dir, exist_ok=True)
os.makedirs(inputs_dir, exist_ok=True)

example_output_file = f'{metadata_dir}/BL_{parent_setting}_{turn}-turns_{amount}-ex_{part}_examples_openai.jsonl'
batch_output_file = f'{inputs_dir}/BL_{parent_setting}_{turn}-turns_{amount}-ex_{part}_batch_openai.jsonl'


#if turn == 5 or turn == 10:
#    participant_num_lst = [1,2]
#    print(f"Turn is {turn} so up to 2 additional participants")
#else:
#    sys.exit("Invalid number of turns")

def GPT4_loop(example_output_file,batch_output_file):
    #example_lst = []
    #batch_lst = []
    
    for counter in tqdm(range(amount)):
        #participant_num = random.choice(participant_num_lst)
        #participants = random.sample(participant_lst,k=participant_num) #ensures no replacement/duplicates           
        #participants = ','.join(participants)
        age = random.choice(age_list)
        if age in [10, 15]:
            verbs, nouns, adjectives = aoa_verbs, aoa_nouns, aoa_adjs
            word_source = "AoA"
        else:
            verbs, nouns, adjectives = wb_verbs, wb_nouns, wb_adjs
            word_source = "Wordbank"
        type = random.choice(type_lst)

        verb = random.choice(verbs)
        noun = random.choice(nouns)
        adjective = random.choice(adjectives)
        child_type = 'toddler' if age==2 else 'child' if age in [5,10] else 'teenager'

        if setting == 'home':
            setting_explained = 'home'
            not_setting = 'public (school or community)'
        else:
            setting_explained = 'public (school or community)'
            not_setting = 'home'
        
        message = [{
            "role": "user",
            "content": 
           (
f"Please construct a realistic, approximately {turn}-turn dialogue directly involving a {age}-year-old "
f"{child_type} as a participant. The {child_type} is the central participant, and most/all speech should be directed towards them. "
f"Use only vocabulary that a typical {age}-year-old {child_type} would understand. "
f"The parent participant and the setting are fixed for this dialogue and must be: **{parent.capitalize()} in a {setting_explained} environment**. "
f"The dialogue must take place entirely in a {setting_explained} environment, with physical, social, or sensory details that make it impossible to mistake for a {not_setting} environment."
f"The topic doesn’t need to be about {setting_explained}, but all lines should naturally reference people, activities, or surroundings specific to this setting. "
f"Include at least two clear details that could not occur in a {not_setting} environment."
f"The dialogue should be {type} and must include the verb '{verb}', the noun '{noun}', and the adjective '{adjective}'. "
f"Strictly do not use or invent any proper names for any participant or in the dialogue. "
f"Use only the labels **{parent.capitalize()}** and **Child** when referring to participants. "
f"Ensure that at least {turn} turns of direct speech are included under the 'DIALOGUE:' section (no summaries or narration in place of dialogue). "
f"Participant labels must be surrounded by double asterisks, e.g., '**participant**'. "
f"Output must strictly follow this format:\n\n"
f"PARTICIPANTS:\n[List and describe only **{parent.capitalize()}** and **Child** without names]\n\n"
f"SETTING:\n[Briefly describe the context/setting]\n\n"
f"DIALOGUE:\n[List {turn} turns of dialogue separated by '\\n\\n']\n\n"
f"Remember, the dialogue must be realistic and likely to occur in the real world."
)
        }]

        ex_ID = f"BL_{parent_setting}_{turn}-turns_{part}_ex-{counter}"
        
        example = {}
        example["custom_id"] = ex_ID
        example['turn'] = turn
        example['age'] = age
        #example['word_source'] = word_source
        #example['participant_num'] = participant_num
        #example['participants'] = participants
        example['type'] = type
        example['verb']= verb
        example['noun'] = noun
        example['adjective'] = adjective
        example['parent'] = parent
        example['setting'] = setting
        #example['location'] = location
        #example_lst.append(example)
        
        batch_example = {}
        batch_example["custom_id"] = ex_ID
        batch_example["method"] = "POST"
        batch_example["url"] = "/v1/chat/completions"
        batch_example["body"] = {}
        batch_example["body"]["model"] = model_deployment_name
        batch_example["body"]["messages"] = message
        batch_example["body"]["max_tokens"] = 2000
        batch_example["body"]["temperature"] = 0.5
        #batch_lst.append(batch_example)

        with open(example_output_file, 'a') as ex_out_f:
            json.dump(example, ex_out_f)
            ex_out_f.write('\n')
        ex_out_f.close()

        with open(batch_output_file, 'a') as batch_out_f:
            json.dump(batch_example, batch_out_f)
            batch_out_f.write('\n')
        batch_out_f.close()

GPT4_loop(example_output_file,batch_output_file)