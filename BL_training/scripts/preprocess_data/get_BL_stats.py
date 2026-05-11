from collections import Counter
import nltk

#nltk.download("punkt", quiet=True)
#from nltk.tokenize import word_tokenize

def compute_stats(path):
    total_words = 0
    total_utts = 0
    whitespace_vocab = Counter()
    nltk_vocab = Counter()
    num_convos = 0

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    conversations = text.split("<|endoftext|>")

    for convo in conversations:
        convo = convo.strip()
        if not convo:
            continue

        num_convos += 1

        utterances = [u.strip() for u in convo.split("\n") if u.strip()]
        total_utts += len(utterances)

        for utt in utterances:
            # whitespace words
            words = utt.split()
            total_words += len(words)
            whitespace_vocab.update(words)

            # nltk tokens
            #tokens = word_tokenize(utt)
            #nltk_vocab.update(tokens)

    return {
        "Conversations": num_convos,
        "Total Words": total_words,
        "Unique Words (Whitespace)": len(whitespace_vocab),
        "Unique Tokens (NLTK)": len(nltk_vocab),
        "Avg. Utterances per Convo": total_utts / num_convos,
        "Avg. Words per Utterance": total_words / total_utts,
        "Avg. Words per Convo": total_words / num_convos,
    }

print(compute_stats("/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_txt_nosplit/eng_topline.txt"))