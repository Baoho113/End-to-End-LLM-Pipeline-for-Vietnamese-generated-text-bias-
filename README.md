# End-to-End LLM Pipeline for Vietnamese Generated Text Bias
## Overview
This project presents an end-to-end Large Language Model (LLM) pipeline designed to detect, analyze, and evaluate bias in Vietnamese AI-generated text. The system focuses on identifying potential social, cultural, gender, and linguistic biases produced by generative AI models in Vietnamese language contexts.

The pipeline integrates data collection, preprocessing, model evaluation, bias detection, and reporting into a complete workflow that supports responsible AI research and development.


## Usage

### Step 1 — Train the model
```bash
python run_train.py
```
This reads `data/vietnamese_bias_claude.csv`, trains the classifier,
and saves the model to `models/bias_detector.pkl`.

### Step 2 — Evaluate an LLM
```bash
# Set your API key first
export ANTHROPIC_API_KEY=sk-ant-...

python run_evaluate_llm.py
```
This sends test prompts to the LLM, collects outputs,
runs them through the detector, and exports results to `outputs/`.

### Step 3 — Evaluate custom texts (no LLM needed)
```python
python run_custom.py --text "Phụ nữ không nên làm giám đốc."
python run_custom.py --text "Người miền Trung nói giọng khó nghe." --mitigate --no-llm

python run_custom.py --file my_outputs.txt
python run_custom.py --file my_outputs.txt --mitigate --export
```

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
