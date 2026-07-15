# End-to-End LLM Pipeline for Vietnamese Generated Text Bias
## Overview
This project presents an end-to-end Large Language Model (LLM) pipeline designed to detect, analyze, and evaluate bias in Vietnamese AI-generated text. The system focuses on identifying potential social, cultural, gender, and linguistic biases produced by generative AI models in Vietnamese language contexts.

The pipeline integrates data collection, preprocessing, model evaluation, bias detection, and reporting into a complete workflow that supports responsible AI research and development.


## Features

* Vietnamese text preprocessing and cleaning
* AI-generated text bias analysis
* Bias classification and evaluation pipeline
* Dataset preparation and transformation
* Support for multiple LLM outputs
* Modular and scalable architecture
* Visualization and reporting of bias metrics
* End-to-end automation workflow

## Project Objectives

The main goals of this project are:

1. Detect bias in Vietnamese generated text.
2. Evaluate fairness and neutrality of LLM outputs.
3. Build an automated pipeline for bias analysis.
4. Support ethical AI research for Vietnamese NLP applications.
5. Provide measurable metrics for model evaluation.


## Tech Stack

### Programming Languages

* Python
* SQL (optional for data storage)

### Frameworks & Libraries

* Transformers
* PyTorch / TensorFlow
* Hugging Face
* Pandas
* NumPy
* Scikit-learn
* Matplotlib / Seaborn
* FastAPI or Flask (if API integration is included)

### Tools

* Jupyter Notebook
* Git & GitHub
* Docker (optional)
* VS Code

---

## System Architecture

The pipeline consists of the following stages:

1. **Data Collection**

   * Gather Vietnamese datasets and AI-generated text samples.

2. **Data Preprocessing**

   * Text cleaning
   * Tokenization
   * Normalization
   * Stop-word handling

3. **LLM Text Generation**

   * Generate Vietnamese text using selected language models.

4. **Bias Detection & Analysis**

   * Evaluate outputs for bias patterns.
   * Measure fairness and harmful stereotypes.

5. **Evaluation Metrics**

   * Accuracy
   * Precision
   * Recall
   * F1-score
   * Bias score

6. **Visualization & Reporting**

   * Generate charts, summaries, and reports.
---

## Example Workflow

1. Import Vietnamese datasets.
2. Generate text using selected LLMs.
3. Preprocess and normalize outputs.
4. Detect bias indicators.
5. Evaluate fairness metrics.
6. Visualize and report findings.

---

## Getting Started: Bias Detection Module

The detection module (`dataset/` + `src/training/`) fine-tunes PhoBERT to classify a Vietnamese sentence into one of 13 categories defined in `docs/annotation_guideline.md` (Non-bias, Gender Bias, Age Bias, Class/Socioeconomic Bias, Occupation Bias, Educational Bias, Religion/Belief Bias, Ethnicity Bias, Marital/Family Status Bias, Political Bias, Mental Health Bias, Appearance Bias, Regional Bias). All commands below are run from the repo root.

### 1. Setup

```bash
pip install -r requirements.txt
```

### 2. Rebuild the dataset splits

Only needed once, or again after editing `dataset/raw/vietnamese_bias_dataset.csv`. Dedupes the raw data, builds a leak-free stratified 80/10/10 train/val/test split, and regenerates `dataset/metadata/label_mapping.json`.

```bash
python dataset/build_splits.py
```

### 3. Train

```bash
python src/training/train_phobert.py
```

Reads `dataset/processed/{train,val}.csv`, fine-tunes PhoBERT-base with class weighting to counter label imbalance, and saves the checkpoint to `checkpoints/phobert_bias_classifier/` (~75 min on CPU; gitignored — not committed, so this step must be run locally or the checkpoint shared separately).

### 4. Evaluate

```bash
python src/training/evaluate.py
```

Runs the checkpoint against the held-out `dataset/processed/test.csv` and prints a full classification report (precision/recall/F1 per category, macro/weighted averages) plus a confusion matrix.

### 5. Detect

Single sentence:

```bash
python src/training/inference_test.py "Người già thường khó tiếp thu."
```

Mass detect over a file — a `.txt` (one sentence per line) or a `.csv` with a `text` column:

```bash
python src/training/inference_test.py --file sentences.txt
python src/training/inference_test.py --file input.csv --out results.csv
```

Without `--out`, results print as JSON (label, confidence, full per-category probability distribution). With `--out`, a `text,label,confidence,labels` CSV is written instead.

The model is trained single-label (see "Known limitation" below), but every result also includes a `labels` list — every category whose score clears `--threshold` (default `0.2`), sorted by confidence, so sentences that plausibly touch more than one category (e.g. both Gender Bias and Occupation Bias) surface all of them instead of only the single winner:

```bash
python src/training/inference_test.py "..." --threshold 0.2
```

This is a threshold heuristic on top of the single softmax output, not an independently-trained multi-label model — scores compete and sum to 1, so a very confident top label naturally suppresses the rest. Tune `--threshold` down to surface more secondary labels, or up to only flag genuinely close calls.

### 6. Serve over HTTP (for the UI)

```bash
uvicorn serve:app --reload --port 8000 --app-dir src/training
```

Exposes `POST /detect`, `POST /detect/batch`, `GET /metrics` (reads `checkpoints/phobert_bias_classifier/eval_metrics.json`, written by `evaluate.py`), and `GET /health`. `--app-dir src/training` is required — it lets uvicorn import `serve.py` without changing the process's working directory, so `config.py`'s repo-root-relative paths still resolve correctly.

### Known limitation

`dataset/raw/vietnamese_bias_dataset.csv` is template-generated and duplicate-heavy (12,499 rows but only 4,277 unique sentences, several categories with as few as 25 uniques). The classifier scores ~99% macro F1 on the (now leak-free) test set, but that reflects near-perfect performance on in-template phrasing, not general Vietnamese text — confidently wrong predictions have been observed on plain neutral sentences outside the training templates. Treat current metrics as a pipeline-correctness check, not a production accuracy number, until the dataset is expanded with more diverse, non-templated examples.

---

## Research & Ethical Considerations

This project supports responsible AI development by:

* Promoting fairness in Vietnamese NLP systems
* Identifying harmful stereotypes in generated text
* Encouraging ethical AI evaluation practices
* Improving transparency in LLM outputs

---

## Future Improvements

* Real-time bias monitoring dashboard
* Expanded Vietnamese datasets
* Multi-model comparison framework
* Integration with multilingual LLMs
* Explainable AI (XAI) features
* Web-based visualization interface

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Push to your branch
5. Open a pull request

---

## License

This project is licensed under the MIT License.

---

## Author

Developed by RMIT students as Capstone Project.

---
