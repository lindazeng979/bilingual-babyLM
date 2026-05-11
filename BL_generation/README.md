# Data Generation Pipeline for bilingual-babyLM

> Most users do **not** need to run this pipeline.

We already provide:
- the raw processed bilingual dialogue dataset
- the exact final training-condition datasets used in the paper

All datasets are available on Hugging Face:
[lindazeng979/bilingual-babyLM](https://huggingface.co/datasets/lindazeng979/bilingual-babyLM), which includes:

| File | Description |
|---|---|
| `bilingual-babyLM.jsonl` | Raw parallel English, Spanish, intersentential, and intrasentential dialogue dataset |
| `BL_conditions.zip` | Main experimental training conditions (~100M-word conditions) |
| `BL_conditions_20M.zip` | Reduced-data 20M-word experimental conditions |

The zip archives already contain the final train/validation splits for all training conditions used in the paper. In most cases, all you need to do is unzip the datasets and train the models.

This README is primarily intended for users who want to:
- reproduce the full generation pipeline
- regenerate datasets
- modify conditions
- create new multilingual mixtures
- inspect intermediate processing steps

---

## Overview

The overall workflow for generating datasets across conditions is reflected in the pipeline structure:

```text id="5zpx0s"
prompt → openai → merge → preprocess → conditions → split → convert
```


**`prompt/`** Prepare prompts and metadata for OpenAI generation.

**`openai/`** Submit and retrieve OpenAI Batch API jobs.

**`merge/`** Merge multiple OpenAI batch outputs into unified datasets.

**`preprocess/`** Clean and normalize generated outputs, such as malforned generations and metadata cleanup.

**`conditions/`** Construct experimental training conditions used in the paper.

**`split/`** Create consistent train/validation splits across all conditions.

**`convert/`** Convert `.jsonl` datasets into raw `.txt` files used for model training.

---

## Repository Structure

The generation pipeline processes data into:

```text id="5f9gnq"
BL_collection_data/
```

Key folders include:

```text id="4e5clu"
BL_collection_data/
├── all/
├── all_processed/
├── all_experiments/
├── all_split_exp/
├── all_split_txt/
├── all_split_txt_20M/
├── english/
├── spanish/
├── intersent/
├── intrasent/
├── AoA_norms/
├── wordbank_CDI_vocab/
```
> Most of these folders do not appear because they are currently empty.

### Important Folders

| Folder | Description |
|---|---|
| `all_processed/` | Fully processed parallel bilingual dataset (merged and released on Hugging Face) |
| `all_experiments/` | Experimental condition `.jsonl` files before being split |
| `all_split_exp/` | Train/validation splits in `.jsonl` format |
| `all_split_txt/` | Final `.txt` training files used for experiments |
| `all_split_txt_20M/` | Reduced-data 20M training conditions |

The final released datasets correspond primarily to:

```text id="2x7v1i"
all_split_txt/
all_split_txt_20M/
```

### Raw Generation Folders

Intermediate generation folders such as:

```text id="qfjlwm"
english/
spanish/
intersent/
intrasent/
```

may contain subdirectories such as:

```text id="5uxqiu"
momhome/
dadhome/
momcommunity/
dadcommunity/
```

Each typically contains:

```text id="z2n4l8"
metadata/
inputs/
outputs/
```

---

## Condition Name Mapping

The following names correspond to the experimental conditions described in the paper:

| Paper Name | Folder Name |
|---|---|
| English Topline | `eng_topline` |
| Spanish Topline | `sp_topline` |
| English Baseline (Mom) | `baseline_speaker_mom_en` |
| English Baseline (Dad) | `baseline_speaker_dad_en` |
| English Baseline (random) | `baseline_random_split` |
| Multilingual (Mom) | `speaker_mom_en` |
| Multilingual (Dad) | `speaker_dad_en` |
| Multilingual (random) | `random_split` |
| Code-switching (sentence-level) | `intersent` |
| Code-switching (word-level) | `intrasent` |

We additionally organize dialogues by conversational setting/context (`home`, `community`), though these distinctions are not emphasized in the paper. We postfix `_20M` to all of the above folder names for reduced-size experiments.

---

## Environment Setup

```bash id="dwdof6"
conda activate py312

pip install transformers torch sil-machine accelerate tqdm
```

We additionally include processed AoA and Wordbank vocabulary resources used during prompting. No additional preprocessing is required for these resources.

---

## Running the Pipeline

The pipeline proceeds in four major stages:

1. English dialogue generation
2. Spanish translation/generation
3. Intra-sentential code-switching generation
4. Inter-sentential code-switching generation

followed by:
- preprocessing
- condition construction
- train/validation splitting
- conversion to training text

---

## English Dialogue Generation

### 1. Metadata Preparation

```bash id="6czskh"
python3 BL_generation/prompt/BL_english_batch_prep.py \
  <model> \
  <turns> \
  <examples> \
  <batch_name> \
  <parent> \
  <setting>
```

Example:

```bash id="lh8bx0"
python3 BL_generation/prompt/BL_english_batch_prep.py \
  gpt-4o-mini-2024-07-18 \
  5 \
  20000 \
  batch1 \
  mom \
  home
```
> Note: This script is repeatedly run for numerous batches to reach the desired generated data size.

This step generates:
- metadata files
- OpenAI batch request files

inside folders such as:

```text id="h2n8ps"
BL_collection_data/english/momhome/
```


### 2. Submit OpenAI Batch Jobs

```bash id="80dt95"
bash BL_generation/openai/run_openai_batches.sh \
  <input_directory> \
  <log_file>
```
Example:
```bash
bash BL_generation/openai/run_openai_batches.sh \
  BL_collection_data/english/momhome \
  BL_collection_data/english/momhome/mapping.txt 
```

### 3. Retrieve Batch Results

```bash id="1d4iq3"
bash BL_generation/openai/retrieve_openai_batch_results.sh \
  <log_file> \
  <output_directory>
```
Example:
```bash
bash BL_generation/openai/retrieve_openai_batch_results.sh \
  BL_collection_data/english/momhome/mapping.txt \
  BL_collection_data/english/momhome &&
```



### 4. Merge Batch Outputs

```bash id="y7cldy"
python3 BL_generation/merge/openai_merge_batches.py
```
Inspect and modify this file in case batch generation was performed differently.

### 5. Preprocess Outputs

```bash id="i3n2fe"
python3 BL_generation/preprocess/openai_preprocess_json.py \
  <outputs_dir> \
  <output_jsonl> \
  <output_txt>
```
Example:
```bash
python3 BL_generation/openai_preprocess_json.py \
  BL_collection_data/english/momcommunity/outputs \
  BL_collection_data/english/momcommunity/BL_momcomm_test_outputs.jsonl \
  BL_collection_data/english/momcommunity/BL_momcomm_test_dialogues.txt  
```
---

## Spanish and Intrasentential Code-Switching Generation

The Spanish and code-switching pipelines closely mirror the English pipeline. The below five steps must be repeated for both spanish and intrasentential code-switching.

### Step 1: Metadata Generation
Metadata generation scripts include:

```text id="xw4z4n"
BL_generation/prompt/BL_spanish_batch_prep.py
BL_generation/prompt/BL_intrasent_batch_prep.py
```

> Note: these scripts do not take in the same arguments as `BL_english_batch_prep.py`, which must be repeated a large amount of times to generate sufficient data. These two scripts only require the generated English dialogues since they involve translation.

Example usage:
```bash
BL_generation/prompt/BL_spanish_batch_prep.py \
 BL_collection_data/english/momhome/outputs \
 BL_collection_data/spanish/momhome/inputs \
 gpt-4o-mini-2024-07-18
```
This should be repeated for `dadhome`, `dadcommunity`, `momcommunity`.

### Steps 2-5: Generate Dialogues using OpenAI
Repeat Steps 2–5 from the English pipeline (OpenAI batch submission, retrieval, merging, and preprocessing), modifying the directories accordingly.

### Additional Preprocessing Notes

A small number of intrasentential examples were manually removed after inspection due to formatting or generation-quality issues:

```text id="4xx7kz"
BL_dadcommunity_5-turns_batch5_ex-5839
BL_dadhome_5-turns_batch4_ex-3342
BL_momcommunity_5-turns_batch2_ex-7983
```


## Intersentential Code-Switching Generation

Intersentential code-switching is generated directly from the processed English and Spanish outputs in the `prompt` stage using regex (no GPT-4 generation). It must be run after both English and Spanish generation are complete.


Example:
```
python3 BL_generation/openai/BL_intersent_batch_generate.py \
  BL_collection_data/english/momhome/BL_momhome_test_outputs.jsonl \
  BL_collection_data/spanish/momhome/BL_momhome_test_outputs.jsonl \
  BL_collection_data/intersent/BL_momhome_test_outputs.jsonl \
  BL_collection_data/all/BL_momhome_test_outputs.jsonl
```

This should be repeated for `dadhome`, `dadcommunity`, `momcommunity`.

---
## Preprocessing Combined Parallel Data

After English, Spanish, and intersentential generation are complete, we reprocess the combined multilingual files into unified parallel examples.

This step creates files in `BL_collection_data/all_processed/` containing aligned English, Spanish, intersentential code-switching variants within the same example.

> Note: Intrasentential data is processed separately later.

Example:

```bash id="u5a7zb"
python3 BL_generation/preprocess/preprocess.py \
  BL_collection_data/all/BL_momhome_test_outputs.jsonl \
  BL_collection_data/all_processed
```

Repeat for `momhome`, `dadhome`, `momcommunity`, `dadcommunity`.

---

## Constructing Experimental Conditions

Experimental training conditions are generated using scripts in:

```text id="ijpd7i"
BL_generation/conditions/
```

These scripts construct the exact training conditions used in the paper.

### Main Experimental Conditions (~100M)

#### English Topline

```bash id="djwz06"
python3 BL_generation/conditions/BL_prepare_exp.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments \
  --make_mix eng_topline \
  --comp dadhome:en \
  --comp momhome:en \
  --comp dadcomm:en \
  --comp momcomm:en \
  --max_total 1000000
```

#### Intersentential Code-switching

```bash id="9qb6zs"
python3 BL_generation/conditions/BL_prepare_exp.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments \
  --make_mix intersent \
  --comp dadhome:intersent \
  --comp momhome:intersent \
  --comp dadcomm:intersent \
  --comp momcomm:intersent \
  --max_total 1000000
```

#### Multilingual (Speaker-Conditioned)

Example: `speaker_mom_en`

```bash id="zwfhrk"
python3 BL_generation/conditions/BL_prepare_exp.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments \
  --make_mix speaker_mom_en \
  --comp dadhome:es \
  --comp momhome:en \
  --comp dadcomm:es \
  --comp momcomm:en \
  --max_total 1000000
```

#### English Baseline

Example: `baseline_speaker_mom_en`

```bash id="d6u9fi"
python3 BL_generation/conditions/BL_prepare_exp.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments \
  --make_mix baseline_speaker_mom_en \
  --comp momhome:en \
  --comp momcomm:en \
  --max_total 1000000
```

Repeat similarly for the remaining experimental conditions.



#### Separately Constructed Conditions

Some conditions use separate scripts:

| Condition | Script |
|---|---|
| `intrasent` | `intrasent_concatenate.py` |
| `random_split` | `BL_prepare_exp_rand.py` |
| `baseline_random_split` | `BL_prepare_exp_rand_distill.py` |

Example:

```bash id="k75zkm"
python3 BL_generation/conditions/BL_prepare_exp_rand.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments \
  --make_balanced_en_es random_split \
  --balanced_max_per_lang 500000 \
  --shuffle \
  --seed 42
```


### Reduced-Data Conditions (20M)

Reduced-data conditions are generated similarly using:

```text id="6qjlwm"
BL_prepare_exp_customsize.py
```

Example:

```bash id="tdr46j"
python3 BL_generation/conditions/BL_prepare_exp_customsize.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments_20M \
  --make_mix eng_topline_20M \
  --comp dadhome:en \
  --comp momhome:en \
  --comp dadcomm:en \
  --comp momcomm:en \
  --lines_per_component 38000 \
  --shuffle \
  --seed 42
```

Special scripts are again used for:

- `intrasent_20M`
```bash id="i7p2is"
python3 BL_generation/conditions/BL_filter_intrasent_20M.py
```
- `random_split_20M`
```bash id="i7p2is"
python3 BL_generation/conditions/BL_prepare_exp_rand_20M.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments \
  --make_balanced_en_es random_split_20M \
  --balanced_max_per_lang 38000 \
  --shuffle \
  --seed 42
```
- `baseline_random_split_20M`
```bash id="i7p2is"
python3 BL_generation/conditions/BL_prepare_exp_rand_distill_20M.py
```

### Varying Exposure Conditions

Varying exposure multilingual conditions are generated by adjusting the Spanish mixing proportion.

Example: 25% Spanish exposure

```bash id="sqt94y"
python3 BL_generation/conditions/BL_prepare_exp_rand.py \
  --input_dir BL_collection_data/all_processed \
  --out_dir BL_collection_data/all_experiments \
  --make_mixed_en_es 25_random_split \
  --shuffle \
  --seed 42 \
  --mixing_proportion 0.25
```

Repeat for `0.10`, `0.25`, `0.75`, `0.90`

Baseline versions are generated similarly using `--make_mixed_en_es_nosp`.

---

## Split into Train / Validation Data

Validation splits use the same data points(ids) as val to make sure it is controlled. 

### Build Master Validation IDs

```bash id="v6t4h9"
python3 BL_generation/split/openai_make_consistent_val.py \
  --build-master \
  --reference BL_collection_data/all_experiments/eng_topline.jsonl \
  --master-out BL_collection_data/all_split_exp/val_ids_master.txt \
  --val-pct-total 0.05 \
  --seed 42
```

Using the same script, separate master validation lists are created for main experiments and 20M conditions.

### Apply Validation Splits

Example:

```bash id="xzc7sn"
python3 BL_generation/split/openai_make_consistent_val.py \
  --apply-master \
  --input BL_collection_data/all_experiments/eng_topline.jsonl \
  --val-idlist BL_collection_data/all_split_exp/val_ids_master.txt \
  --outdir BL_collection_data/all_split_exp/eng_topline/
```

Repeat for each condition, including varying exposure experiments.

Some conditions (e.g. `intrasent`, `baseline_random_split`) use separate splitting scripts:

```bash
python3 BL_generation/split/intrasent_val_split \
  --apply-master \
  --input BL_collection_data/intrasent/intrasent.jsonl \
  --val-idlist BL_collection_data/all_split_exp/val_ids_master.txt \
  --outdir BL_collection_data/all_split_exp/intrasent/
```

---

## Converting to Text Files

Final model-training text files are generated using:

```bash id="x5u48v"
python3 BL_generation/convert/extract_all_split.py \
  BL_collection_data/all_split_exp \
  BL_collection_data/all_split_txt
```

Reduced-data version:

```bash id="s0nb9t"
python3 BL_generation/convert/extract_all_split.py \
  BL_collection_data/all_split_exp_20M \
  BL_collection_data/all_split_txt_20M
```


### Intrasentential Additional Preprocessing

Intrasentential conditions require additional preprocessing before conversion into final `.txt` files. Temporarily move `val.json` out of `BL_collection_data/all_split_exp/intrasent` and run:

```bash id="lxyj8y"
python3 BL_generation/openai_preprocess_json_intrasent.py \
  BL_collection_data/all_split_exp/intrasent \
  BL_collection_data/all_split_txt/intrasent/unused.jsonl \
  BL_collection_data/all_split_txt/intrasent/train.txt
```

Delete `BL_collection_data/all_split_txt/intrasent/unused.jsonl`.

Move `val.json` back, temporarily move `train.json` out of `BL_collection_data/all_split_exp/intrasent`, and run:

```bash id="lxyj8y"
python3 BL_generation/openai_preprocess_json_intrasent.py \
  BL_collection_data/all_split_exp/intrasent \
  BL_collection_data/all_split_txt/intrasent/unused.jsonl \
  BL_collection_data/all_split_txt/intrasent/val.txt
```
Delete `BL_collection_data/all_split_txt/intrasent/unused.jsonl`.

## Final Outputs

The final released training datasets correspond to:

```text id="o8d0t7"
BL_collection_data/all_split_txt/
BL_collection_data/all_split_txt_20M/
```

Each condition folder contains:

```text id="1av9mf"
train.txt
val.txt
```

These are the exact text datasets used for model training in the paper and can be copied over to training:
```bash
cp -r BL_collection_data/all_split_txt/* BL_training/data/
cp -r BL_collection_data/all_split_txt_20M/* BL_training/data/
```
---

## Citation

This is part of the larger [bilingual-babyLM](https://github.com/lindazeng979/bilingual-babyLM) directory. If you use this repository, dataset, training conditions, or code in your work, please cite:

```bibtex

@article{zeng2026bringing,
  title={Bringing Up a Bilingual BabyLM: Investigating Multilingual Language Acquisition Using Small-Scale Models},
  author={Zeng, Linda and Feng, Steven Y. and Frank, Michael C.},
  journal={arXiv preprint arXiv:2603.29552},
  year={2026}
}
