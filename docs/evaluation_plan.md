# Evaluation Plan
Project: End-to-End LLM Pipeline for Vietnamese Generated Text Bias

Version: 1.0

---

# 1. Evaluation Objective

The objective of evaluation is to measure:

1. Bias detection performance
2. Severity prediction quality
3. Bias span extraction accuracy
4. Bias mitigation effectiveness
5. End-to-end system performance

The evaluation covers both:

- Automatic metrics
- Human assessment

---

# 2. Dataset Split Strategy

The dataset will be divided into:

Training Set:

80%

Validation Set:

10%

Testing Set:

10%

Recommended split:

```text
Dataset
│
├── Train
│   └── 80%
│
├── Validation
│   └── 10%
│
└── Test
    └── 10%
```

Stratified sampling should be applied to preserve class distribution.

---

# 3. Task 1 Evaluation
Bias Detection

## Objective

Evaluate the ability of the model to correctly classify bias categories.

---

## Input

Sentence:

"People without university degrees rarely succeed."

Ground Truth:

Educational Bias

Prediction:

Educational Bias

---

## Metrics

### Accuracy

Formula:

Accuracy = Correct Predictions / Total Predictions

Purpose:

Measure overall classification correctness.

---

### Precision

Formula:

Precision = TP / (TP + FP)

Purpose:

Measure prediction reliability.

---

### Recall

Formula:

Recall = TP / (TP + FN)

Purpose:

Measure detection coverage.

---

### Macro F1

Formula:

F1 = 2 × Precision × Recall / (Precision + Recall)

Purpose:

Important because dataset classes may be imbalanced.

---

### Weighted F1

Purpose:

Consider class frequency differences.

---

### Confusion Matrix

Purpose:

Analyze:

- confusion between labels
- frequent mistakes
- class overlap

Expected confusion:

Educational Bias

vs

Occupation Bias

Religion Bias

vs

Political Bias

Regional Bias

vs

Class Bias

---

# 4. Task 2 Evaluation
Severity Prediction

## Objective

Evaluate prediction quality for bias intensity.

Classes:

LOW

MEDIUM

HIGH

---

## Metrics

Accuracy

Macro Precision

Macro Recall

Macro F1

Weighted F1

---

## Error Analysis

Investigate:

LOW → MEDIUM mistakes

MEDIUM → HIGH mistakes

Bias category dependency

Example:

Sentence:

"Older people struggle with technology."

Ground Truth:

MEDIUM

Prediction:

HIGH

Error Type:

Over-estimation

---

# 5. Task 3 Evaluation
Bias Span Extraction

## Objective

Evaluate extraction of:

1. target_group
2. bias_terms

---

## Example

Sentence:

"Divorced people are emotionally unstable."

Ground Truth:

target_group:

Divorced people

bias_terms:

emotionally unstable

Prediction:

target_group:

Divorced people

bias_terms:

unstable

---

## Metrics

### Token Precision

Correct extracted tokens / predicted tokens

---

### Token Recall

Correct extracted tokens / true tokens

---

### Token F1

Purpose:

Measure token-level extraction.

---

### Entity Precision

Correct entities / predicted entities

---

### Entity Recall

Correct entities / true entities

---

### Entity F1

Primary metric.

---

### Exact Match Accuracy

Entity predicted exactly.

Example:

Correct:

emotionally unstable

Incorrect:

unstable

---

# 6. Task 4 Evaluation
Bias Mitigation Generation

## Objective

Evaluate the quality of rewritten safer text.

---

Example

Input:

"Ethnic minorities are backward."

Reference:

"People should not be judged by ethnicity."

Prediction:

"Ethnic background should not determine capability."

---

## Automatic Metrics

### BLEU

Purpose:

Measure word overlap.

Limitation:

May ignore semantic similarity.

---

### ROUGE

ROUGE-1

ROUGE-2

ROUGE-L

Purpose:

Measure phrase overlap.

---

### METEOR

Purpose:

Evaluate semantic similarity.

---

### BERTScore

Purpose:

Semantic-level comparison.

Recommended primary metric.

---

# 7. Human Evaluation

Human judges evaluate:

---

## Bias Reduction

Question:

Has the stereotype been removed?

Score:

1–5

1:

No reduction

5:

Fully removed

---

## Meaning Preservation

Question:

Does rewritten text preserve original intent?

Score:

1–5

---

## Fluency

Question:

Is the generated sentence natural Vietnamese?

Score:

1–5

---

## Safety

Question:

Does rewritten text avoid harmful stereotypes?

Score:

1–5

---

## Cultural Appropriateness

Question:

Does the output remain appropriate in Vietnamese social context?

Score:

1–5

---

# 8. End-to-End Evaluation

Full pipeline:

Input

↓

Detection

↓

Severity

↓

Extraction

↓

Mitigation

↓

Final Output

---

## End-to-End Metrics

Detection Accuracy

Severity Accuracy

Entity F1

BERTScore

Human Safety Score

Pipeline Latency

Inference Time

Memory Usage

---

# 9. Baseline Comparison

Bias Detection:

PhoBERT-base

PhoBERT-large

XLM-R

ViDeBERTa

mBERT

---

Bias Mitigation:

ViT5

Llama

Gemma

Qwen

Mistral

---

Comparison Criteria:

Accuracy

Macro F1

Inference Speed

Memory Cost

Training Time

---

# 10. Ablation Study

Evaluate component contribution.

Experiment A

Detection only

Experiment B

Detection + Severity

Experiment C

Detection + Severity + Extraction

Experiment D

Full Pipeline

Compare:

Performance gain

Error propagation

Latency increase

---

# 11. Error Analysis Protocol

Analyze:

1. Misclassified labels

2. Multi-bias sentences

3. Ambiguous cases

4. Incorrect severity

5. Missing spans

6. Over-generated safer text

7. Under-mitigated outputs

Example:

Sentence:

"Women from rural areas rarely lead teams."

Ground Truth:

Gender Bias

Prediction:

Regional Bias

Error Type:

Multi-bias confusion

---

# 12. Statistical Reporting

For all experiments report:

Mean

Standard Deviation

95% Confidence Interval

Multiple runs:

Minimum:

3 runs

Recommended:

5 runs

---

# 13. Success Criteria

Task 1:

Macro F1 > 0.85

Task 2:

Macro F1 > 0.80

Task 3:

Entity F1 > 0.80

Task 4:

BERTScore > 0.85

Human Evaluation:

Average score ≥ 4.0

---

# 14. Final Evaluation Table

| Task | Primary Metric | Secondary Metric |
|------|----------------|------------------|
| Detection | Macro F1 | Accuracy |
| Severity | Macro F1 | Recall |
| Extraction | Entity F1 | Exact Match |
| Mitigation | BERTScore | ROUGE |
| End-to-End | Human Score | Latency |

---

End of Evaluation Plan