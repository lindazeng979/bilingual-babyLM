with open('/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/intrasent/train.txt', 'r') as f1, open('/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/intrasent/val.txt', 'r') as f2:
    content = f1.read() + f2.read()

with open('/Users/lindazeng/Documents/bilingual-llms/BL_collection_data/all_split_txt/intrasent/combined.txt', 'w') as outfile:
    outfile.write(content)