# bilingual-babyLM

This repository contains the code and data for the paper:

**[Bringing Up a Bilingual BabyLM: Investigating Multilingual Language Acquisition Using Small-Scale Models](https://arxiv.org/abs/2603.29552)**

**Authors:** [Linda Zeng](www.linkedin.com/in/linda-zeng-663aaa2a5), [Steven Y. Feng](http://styfeng.github.io/), [Michael C. Frank](http://web.stanford.edu/~mcfrank/) (Stanford University).

> Please contact lindazeng@stanford.edu if you have any questions or concerns.

---
## 📦 Data

* **Bilingual-BabyLM dataset** is hosted on Hugging Face: [lindazeng979/bilingual-babyLM](https://huggingface.co/datasets/lindazeng979/bilingual-babyLM)
* We release both:
  * the synthetic bilingual dialogue dataset used to construct conditions
  * the exact training condition datasets used in the paper

The exact training condition datasets used in our experiments are provided as:
```bash
BL_conditions.zip
BL_conditions_20M.zip
```
To replicate our training, download these archives from the Hugging Face dataset repository and place them inside:
```bash
BL_training/data/
```

### Data Generation & Modifications
If you would like to access the synthetic bilingual dialogue dataset used to construct conditions and generate your own training conditions using it, the Hugging Face [repo](https://huggingface.co/datasets/lindazeng979/bilingual-babyLM) also includes the raw generated data as `bilingual-babyLM.json`.

This Github repository includes the full data generation pipeline, preprocessing code, and code used to construct our paper's final training conditions. To reproduce or inspect the generation pipeline:

```bash
cd BL_generation
```
Inside `BL_generation`, we provide a separate `README.md` containing detailed instructions for:

* synthetic dialogue generation
* preprocessing
* condition construction
* train/validation splitting

This pipeline loads and processes data into `BL_collection_data`.

Beyond this point, we assume generation is complete and move to the training pipeline in `BL_training`.

### Training Data Setup

To run the training conditions from the paper, unzip the following directories:

```bash
cd BL_training/data

# Main datasets
unzip BL_data_conditions.zip

# Optional: 20M datasets
unzip BL_data_conditions_20M.zip
```

After unzipping, collapse the folder hierarchy so the datasets are directly inside `data/`

Example:

```bash
mv BL_data_conditions/* .
mv BL_data_conditions_20M/* .

rmdir BL_data_conditions
rmdir BL_data_conditions_20M
```

#### Optional: Varying Exposure Experiments

If you plan to run varying exposure experiments:

```bash
# Enter varying exposure directory
cd varying_exposure

# Move files outward into data/
mv * ../

# Return to data directory
cd ..

# Remove empty folder if desired
rmdir varying_exposure
```
Repeat the above with the `baseline_varying_exposure` directory.

After this step, the datasets should be directly accessible from:

```text
BL_training/data/
```

---

## ⚙️ Environment Setup

### Step 1: Install Miniconda (if needed)

Return to the main repository directory and install:

```bash
cd ..
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
export PATH="~/miniconda3/condabin:$PATH"
source ~/.bashrc
conda init
```

### Step 2: Create and Configure Training Environment

```bash
cd BL_training
conda create -n BL_train python=3.10.9
conda activate BL_train
cd transformers
pip install .
cd examples/pytorch/language-modeling
pip install -r requirements.txt
pip install accelerate tokenizers nltk
pip install numpy==1.24.2
pip install wandb
```

### Step 3: Login to Weights & Biases

```bash
wandb login
```

Optional verification:

```bash
ls -l ~/.netrc
cat ~/.netrc
```

### Step 4: Install PyTorch

```bash
pip install --force-reinstall "torch==2.8.0+cu128" \
  --index-url https://download.pytorch.org/whl/cu128
```
> Note: a default version of PyTorch may be installed above. We explicitly reinstall the CUDA-compatible version below to ensure GPU compatibility.

**Optional: Verify Installation**

```bash
python -c "import torch; print(torch.__version__)"
python -c "import transformers; print(transformers.__version__)"
python -c "import numpy; print(numpy.__version__)"
python -c "import accelerate; print(accelerate.__version__)"
nvcc --version
dpkg -l | grep libnccl
```

**Optional: GPU Test Script**

```python
import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))
```

**Optional: CUDA Compatibility Fix**

```bash
pip install torch==2.1.2+cu121 \
  torchvision==0.16.2+cu121 \
  torchaudio==2.1.2+cu121 \
  --extra-index-url https://download.pytorch.org/whl/cu121
```

**Optional: NCCL Multi-GPU Fix**

```bash
sudo apt-get install \
  libnccl2=2.18.3-1+cuda12.1 \
  libnccl-dev=2.18.3-1+cuda12.1
```
---

## 🧪 Model Training

### Tokenizer Training

```bash
python3 scripts/tokenizers/train_GPT2_tokenizer.py \
  <train_file> \
  <val_file> \
  <output_folder> \
  <vocab_size>
python3 scripts/tokenizers/test_GPT2_tokenizer.py <output_folder>
```
> Note: train a tokenizer for every unique dataset that you want to train a model on. Then, make sure to use that tokenizer while training that model on that particular dataset. The default `vocab_size` for GPT-2 is 52k, and our experiments use 80k (see Section 3.3 of our paper).

**Example**:

```bash
python3 scripts/tokenizers/train_GPT2_tokenizer.py \
  data/eng_topline/train.txt \
  data/eng_topline/val.txt \
  tokenizers/eng_topline \
  80000
```

### GPT-2 Training

Training uses a modified version of HuggingFace’s `run_clm.py,` with credit to the [HuggingFace Transformers repository](https://github.com/huggingface/transformers).

**Generic Training Command**:

```bash
bash scripts/language_model_training/GPT2_CHILDES_4-GPUs_train.sh \
  <train_file> \
  <val_file> \
  <tokenizer_folder> \
  <config_folder> \
  <model_output_path> \
  <model_size> \
  <lr> \
  <epochs> \
  <batch_size> \
  <seed>
```

**Example**:

```bash
bash scripts/language_model_training/GPT2_CHILDES_4-GPUs_train.sh \
  data/eng_topline/train.txt \
  data/eng_topline/val.txt \
  tokenizers/eng_topline \
  tokenizers/GPT2-small_config \
  trained_GPT2_models/GPT2-eng_topline \
  gpt2 \
  1e-04 \
  20 \
  8 \
  42
```

Optional logging:

```bash
> eng_topline.log 2>&1
```


**Notes**:

- **Different Experiments**: In the example above, you can replace all occurrences of `eng_topline` with the folder name of a different data condition (e.g. `intrasent`) to run different experiments.
- **Model Size**: You can adjust the `model_size` from `gpt2` to `gpt2-mini` and save to a new model directory while keeping all else the same to replicate our smaller model size experiments.
- **GPU Count**: You can change the number of GPUs by modifying the training script.
- **Checkpoint Saving**: The current script hardcodes `SAVE_TOTAL_LIMIT=2` to reduce storage usage. Modify this if you want more intermediate checkpoints.
- **WandB**: Weights & Biases logging is enabled. You can test WandB setup with:

```bash
python3 scripts/language_model_training/wandb_test.py
```

**Large-Scale Training**:

To train multiple models sequentially:

```bash
bash scripts/language_model_training/run_tests.sh
```

Modify this script to specify data conditions / model names desired to be trained.

---

## 📊 Evaluation

All evaluation datasets included in this repository are already pre-filtered using the vocabulary of the training data. You do **not** need to rerun filtering.

If you are using an new evaluation dataset, please refer to the preprocessing scripts in `BL_training/scripts/preprocess_eval_data/`. We also provide the vocab files used to filter the evaluation data sets in `BL_training/data/`. The exact filtering script depends on the dataset/evaluation condition. The general pipeline is:

1. Run `get_BL_vocab.py` to extract vocabulary from the relevant training data.
2. Run `combine_vocab_files.py` to merge the desired vocabulary files.
3. Run the appropriate `BL_filter<...>.py` script for the target evaluation dataset.


### Perplexity Evaluation

Perplexity evaluation requires the validation sets of the English and Spanish topline conditions and uses the following paths by default:

```python
EN_BASE_PATH = "data/eng_topline/val.txt"
EN_20M_PATH = "data/eng_topline_20M/val.txt"

ES_BASE_PATH = "data/sp_topline/val.txt"
ES_20M_PATH = "data/sp_topline_20M/val.txt"
```

These files should be present if the data setup was performed according to the instructions in this README. If these files are not present, modify the paths in the script `BL_training/scripts/evaluation/eval_ppl.py`. 

**Evaluate Specific Models:**

```bash
python3 scripts/evaluation/eval_ppl.py \
  --models \
  /path/to/model1 \
  /path/to/model2 \
  /path/to/model3
```
> Note: If a model path contains `20M`, the script automatically switches to the corresponding 20M evaluation datasets.

**Evaluate Entire Model Directory:**

```bash
python scripts/evaluation/eval_ppl.py \
  --model-dir /path/to/trained_GPT2_models
```

Results are automatically saved in `BL_training/results/perplexity_eval_results.txt`. You may modify the output directory using `--out-file`.

```bash
python scripts/evaluation/eval_ppl.py \
  --model-dir /path/to/trained_GPT2_models \
  --out-file results/my_results.txt
```

### Word Similarity Evaluation

Based on [LexiContrastiveGrd](https://github.com/EvLab-MIT/LexiContrastiveGrd). Credits to Chengxu Zhuang and coauthors of [arXiv:2310.13257](https://arxiv.org/abs/2310.13257) and [arXiv:2403.14551](https://arxiv.org/abs/2403.14551).

**Setup:**
```
cd LexiContrastiveGrd
conda create -n babyLM_WR python=3.9
conda activate babyLM_WR
pip install -e .
pip install git+https://github.com/chengxuz/lm-evaluation-harness.git
pip install pytest pycountry openpyxl scipy sacrebleu sklearn
```
**Evaluation Command:**
```
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
cd src/llm_devo/word_sim
python eval_word_sim.py \
  --ckpt_path <path_to_model> \
  --output_file <results_txt> \
  --output_csv <results_csv> \
  --output_final_avg_score_csv <avg_csv>
```

**Evalute multiple models**:
```bash
bash scripts/evaluation/eval_ws.sh
```

Modify this script to include the desired `model_names` and global paths if necessary.

### Multilingual Word Similarity Evaluation

Based on the multilingual word similarity datasets from [SemEval-2017 Task 2](https://aclanthology.org/S17-2002.pdf).

**Setup:**
Use the same environment as the Word Similarity evaluation.

```bash
conda activate babyLM_WR
cd LexiContrastiveGrd
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
cd src/llm_devo/word_sim
```
**Evaluation Command:**
```bash
python3 BL_multiling_eval_word_sim.py \
  --ckpt_path <path_to_model> \
  --output_file <results_txt> \
  --output_csv <results_csv> \
  --output_final_avg_score_csv <avg_csv> \
  --word_pairs_file <word_pairs_file> \
  --human_scores_file <human_scores_file> \
  --dataset_name <dataset_name>
```
**Example:**
```bash
python3 BL_multiling_eval_word_sim.py \
  --ckpt_path trained_GPT2_models/GPT2-eng_topline \
  --output_file results/multilingual_wr/results.txt \
  --output_csv results/multilingual_wr/max_layer.csv \
  --output_final_avg_score_csv results/multilingual_wr/final_avg.csv \
  --word_pairs_file SemEval17-Task2/test/subtask1-monolingual/data/en.test.data.txt \
  --human_scores_file SemEval17-Task2/test/subtask1-monolingual/keys/en.test.gold.txt \
  --dataset_name en_test
```
> Note that this only runs results on English word similarity and that it must be repeated for Spanish and English-Spanish, which have paths that can be found in the batch evaluation script below.

**Evaluate multiple models:**
```bash
bash scripts/evaluation/eval_xws.sh
```
Modify this script to include the desired `partial_model_paths` and global path if necessary.


### Zorro Evaluation

This is adapted from the BabyLM workshop's evaluation (2023) [repo](https://github.com/babylm/evaluation-pipeline-2023). Here is the original Zorro [repo](https://github.com/phueb/Zorro).

We have already:
- Preprocessed and filtered Zorro evaluation examples by training data vocabulary
- Converted them to the BLIMP format
- Saved outputs in `evaluation-pipeline/BL-data_zorro_OFFICIAL` and `evaluation-pipeline/BL-data_zorro_OFFICIAL_dialogue-format-BL_Mom`, along with 20M-data corresponding versions. Note that the later directory includes `Mom:` prepended to all evaluation instances.
- Modified scripts accordingly

**Setup:**
```bash
conda create -n babyLM_zorro python=3.9
conda activate babyLM_zorro
cd evaluation-pipeline
pip install -e ".[colab]"
pip install promptsource==0.2.3
pip install numpy==1.24.2
```
**Optional: CUDA compatibility fix**
```bash
pip install torch==1.10.1+cu111 torchvision==0.11.2+cu111 torchaudio==0.10.1 -f https://download.pytorch.org/whl/cu111/torch_stable.html
```

**Optional: Make evaluation scripts executable**
```
chmod u+x finetune_all_tasks.sh
chmod u+x finetune_model.sh
```

**Evaluation command:** 
```bash
python3 babylm_eval_zorro.py \
  <model_path> \
  decoder \
  <eval_format> \
  <results_txt> \
  <final_avg_csv> \
  <results_csv> \
  <results_jsonl>
```
Note that the <eval_format> used in our experiments is `BL-data_zorro_OFFICIAL` or `BL-data_zorro_OFFICIAL_20M` (after filtering).

**Evalute multiple models**:

```bash
bash scripts/evaluation/eval_zorro.sh
```
Modify this script to include the desired `MODEL_NAMES`, `MODEL_DIR`, and output paths if necessary.

---
## 🌌 Embedding Visualizations

We provide a UMAP visualization pipeline for token embedding spaces. Tokens are colored according to empirical language usage estimated from the English-only and Spanish-only corpora (see paper for details).

### Install Visualization Dependencies

(Optional: use a separate environment)

```bash
pip install torch transformers umap-learn plotly
```

### Generate Visualization

Command (replace `<path_to_model>` and `<output_name>`)
```bash
python3 BL_training/scripts/embedding_visualization/wordcloud.py \
  --model_path <path_to_model> \
  --en_txt BL_training/data/eng_topline/train.txt \
  --es_txt BL_training/data/sp_topline/train.txt \
  --out_html BL_training/results/embedding/<output_name>.html \
  --max_lines 200000 \
  --min_count 1 \
  --conf_thresh 0.75 \
  --max_tokens 20000 \
  --keep_space_tokens
```

The generated HTML file will appear in: `BL_training/results/embedding/`. Open the HTML file in a browser to interact with the visualization.

Generation may take some time depending on dataset size.

## 📑 Citation

If you use this codebase or dataset, please cite:

```bash
@article{zeng2026bringing,
  title={Bringing Up a Bilingual BabyLM: Investigating Multilingual Language Acquisition Using Small-Scale Models},
  author={Zeng, Linda and Feng, Steven Y and Frank, Michael C},
  journal={arXiv preprint arXiv:2603.29552},
  year={2026}
}
```
