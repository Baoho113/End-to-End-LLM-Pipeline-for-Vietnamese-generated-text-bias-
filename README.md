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

### 6. Mitigate (AI rewrite)

`src/training/mitigate.py` rewrites a flagged sentence into a safer, non-biased version via an OpenAI-compatible chat API (Task 4, "safer_text", done with a hosted LLM rather than a fine-tuned ViT5 — that's the v2/severity track). It's called through the `POST /mitigate` endpoint added to `serve.py` in step 7, but also has its own small CLI for testing it in isolation.

By default it talks to **RMIT's VAL gateway** (`https://val.rmit.edu.au/api/`, model `openai-gpt-4o`), not OpenAI's own `api.openai.com` — that's what the `VAL-Balam-Key1` Bitwarden item is scoped to, and a plain OpenAI-format key/URL will fail auth against it. Override `OPENAI_BASE_URL` (empty string to hit OpenAI's own API instead) and `MITIGATION_MODEL` if you're using a different provider/account.

The key itself isn't kept in `.env` — it's pulled at request time from your Bitwarden vault via the `bw` CLI:

```bash
npm install -g @bitwarden/cli   # or the standalone binary: https://bitwarden.com/help/cli/
bw login
bw unlock                       # prints an export command with a session key
export BW_SESSION="<session key from the line above>"
```

`bw unlock` needs your master password once per shell — `serve.py` never prompts for it itself, so keep that shell (or export `BW_SESSION` into whichever shell runs uvicorn) unlocked while the detection API is running. It looks up the item named `VAL-Balam-Key1`'s password field by default; override with `OPENAI_BW_ITEM` if you rename it or want to point at a different item (e.g. a personal OpenAI-account key), or set `OPENAI_API_KEY` directly to skip Bitwarden entirely (e.g. in CI). Note: **"View items, hidden passwords" collection permission also blocks CLI/API retrieval, not just the web vault UI** — it's a server-side ACL, not a UI-only restriction, so if `bw get password` fails with "No password available for this login" despite the vault being unlocked, that's the org permission to fix, not a `bw`/env issue.

**Test that the key resolves** (from repo root, no API call, no tokens spent):

```bash
python src/training/mitigate.py
```

Prints a masked key (`sk-proj-...ab12 (164 chars)`) and which source it came from, or a specific error (`bw` missing from PATH, vault locked, item not found/empty/permission-restricted). **Test a full rewrite:**

```bash
python src/training/mitigate.py "Người già thường khó tiếp thu." --label "Age Bias"
```

**Choosing the model/endpoint:** set `MITIGATION_MODEL` and/or `OPENAI_BASE_URL` before starting uvicorn:

```bash
export MITIGATION_MODEL=openai-gpt-4o
export OPENAI_BASE_URL=https://val.rmit.edu.au/api/   # empty string for OpenAI's own api.openai.com
python -m uvicorn serve:app --reload --port 8000 --app-dir src/training
```

or prefix a single test run: `MITIGATION_MODEL=openai-gpt-4o python src/training/mitigate.py "..."`. There's no allow-list — an invalid model name or base URL surfaces as an API error (404/401/etc.) in the response.

### 7. Serve over HTTP (for the UI)

```bash
python -m uvicorn serve:app --reload --port 8000 --app-dir src/training
```

Exposes `POST /detect`, `POST /detect/batch` (legacy single-label PhoBERT classifier), `POST /detect-severity` (the 14-category LoRA-fine-tuned Qwen2.5 model the UI actually calls now, see `src/training/train_llm_lora.py`), `POST /mitigate` (step 6 above), `GET /metrics` (reads `checkpoints/phobert_bias_classifier/eval_metrics.json`, written by `evaluate.py`), and `GET /health`. `--app-dir src/training` is required — it lets uvicorn import `serve.py` without changing the process's working directory, so `config.py`'s repo-root-relative paths still resolve correctly.

If this machine has more than one Python installation (e.g. Anaconda alongside a plain python.org install), make sure the `uvicorn`/`python` you're invoking is the one with `torch`/`transformers`/`peft` installed — `python -m uvicorn` (rather than a bare `uvicorn` on PATH) uses whichever `python` resolves first, which sidesteps picking up a different interpreter that's missing those packages.

### 8. Run the web UI

The UI (`UI/`) is a Next.js app whose home page (`/`) is the Input → Detect → Mitigate → Evaluate analysis tool, talking to the service from step 7. Two terminals, both from the repo root:

**Terminal 1 — detection API** (step 7 above, keep it running):

```bash
python -m uvicorn serve:app --reload --port 8000 --app-dir src/training
```

**Terminal 2 — frontend:**

```bash
cd UI
npm install   # first time only
npm run dev
```

Open **http://localhost:3000**. Start the detection API first (or at least before using the Detect/Mitigate/Evaluate stages) — the UI's `/api/detect`, `/api/mitigate`, and `/api/metrics` routes proxy to `http://localhost:8000` and show a "service unreachable" error if it isn't up yet.

`UI/backend/` (Express + Prisma, its own `npm run dev` on port 3001) is a **separate, unrelated** backend for the old chat/login pages (`/auth`, `/dashboard`), which still exist but aren't linked from the home page. You don't need to run it for the analysis tool above — only if you want to explore that older chat flow.

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
