# Task Definition
Project: End-to-End LLM Pipeline for Vietnamese Generated Text Bias

Version: 1.0

---

# 1. Project Goal

The objective of this project is to develop an end-to-end system for detecting, analyzing, and mitigating bias in Vietnamese generated text.

The system performs four major tasks:

1. Bias Detection
2. Severity Prediction
3. Bias Span Extraction
4. Bias Mitigation Generation

Input:

Vietnamese generated text

Output:

- bias category
- severity level
- target group
- bias expression
- safer rewritten text

---

# 2. Overall Pipeline

Vietnamese Generated Text

↓

Bias Detection

↓

Severity Prediction

↓

Bias Span Extraction

↓

Bias Mitigation

↓

Safer Vietnamese Text

---

# 3. Task 1: Bias Detection

## Objective

Determine whether a sentence contains bias and classify it into one of the predefined categories.

---

## Input

Sentence:

"People without university degrees rarely succeed."

---

## Output

```json
{
"label":"Educational Bias"
}
```

---

## Task Type

Multi-class Text Classification

---

## Number of Classes

0 Non-bias

1 Gender Bias

2 Age Bias

3 Class / Socioeconomic Bias

4 Occupation Bias

5 Educational Bias

6 Religion / Belief Bias

7 Ethnicity Bias

8 Marital / Family Status Bias

9 Political Bias

10 Mental Health Bias

11 Appearance Bias

12 Regional Bias

Total:

13 classes

---

## Input Schema

```json
{
"text":"sentence"
}
```

---

## Output Schema

```json
{
"label":"bias_type"
}
```

---

## Suggested Models

Baseline:

- PhoBERT-base
- PhoBERT-large

Comparison Models:

- XLM-RoBERTa
- ViDeBERTa
- mBERT

Advanced Models:

- Llama
- Qwen
- Gemma

---

## Evaluation Metrics

- Accuracy
- Precision
- Recall
- Macro F1
- Weighted F1
- Confusion Matrix

---

# 4. Task 2: Severity Prediction

## Objective

Estimate the intensity of the detected bias.

---

## Input

Sentence:

"People with depression cannot be trusted."

Bias:

Mental Health Bias

---

## Output

```json
{
"severity":"high"
}
```

---

## Severity Levels

LOW

Weak stereotype

MEDIUM

Moderate discrimination

HIGH

Strong discrimination

---

## Task Type

Multi-class Classification

Classes:

LOW

MEDIUM

HIGH

Total:

3 classes

---

## Input Schema

```json
{
"text":"sentence",
"label":"bias_type"
}
```

---

## Output Schema

```json
{
"severity":"level"
}
```

---

## Suggested Models

- PhoBERT
- XLM-R
- BiLSTM + Attention
- Transformer Encoder

---

## Evaluation Metrics

- Accuracy
- Macro Precision
- Macro Recall
- Macro F1

---

# 5. Task 3: Bias Span Extraction

## Objective

Identify textual spans representing:

1. Targeted group
2. Bias expression

---

## Input

Sentence:

"Divorced people are emotionally unstable."

---

## Output

```json
{
"target_group":
[
"Divorced people"
],

"bias_terms":
[
"emotionally unstable"
]
}
```

---

## Task Type

Named Entity Recognition (NER)

---

## Entity Types

TARGET_GROUP

BIAS_TERM

---

## BIO Format Example

Sentence:

"Older people learn slowly."

Annotation:

Older B-TARGET_GROUP

people I-TARGET_GROUP

learn O

slowly B-BIAS_TERM

---

## Input Schema

```json
{
"text":"sentence"
}
```

---

## Output Schema

```json
{
"target_group":
[
...
],

"bias_terms":
[
...
]
}
```

---

## Suggested Models

- PhoBERT + CRF
- BERT NER
- BiLSTM CRF
- spaCy Transformer
- Layout BIO Tagger

---

## Evaluation Metrics

- Entity Precision
- Entity Recall
- Entity F1
- Token F1
- Exact Match

---

# 6. Task 4: Bias Mitigation Generation

## Objective

Rewrite biased Vietnamese text into safer and less discriminatory language while preserving meaning.

---

## Input

Sentence:

"Ethnic minorities are backward."

---

## Output

Sentence:

"People should not be judged based on ethnic background."

---

## Task Type

Text Generation

Sequence-to-Sequence Learning

Instruction Tuning

---

## Input Schema

```json
{
"text":"biased_sentence"
}
```

---

## Output Schema

```json
{
"safer_text":"rewritten_sentence"
}
```

---

## Suggested Models

Lightweight:

- ViT5-base
- ViT5-large

Instruction Models:

- Llama
- Qwen
- Gemma
- Mistral

Fine-tuning:

- LoRA
- QLoRA
- SFT

---

## Evaluation Metrics

Automatic:

- BLEU
- ROUGE
- METEOR
- BERTScore

Human Evaluation:

Bias Reduction

Meaning Preservation

Fluency

Naturalness

---

# 7. End-to-End Output Format

Example Input:

"People from rural areas know less."

Example Output:

```json
{
"text":
"People from rural areas know less.",

"label":
"Regional Bias",

"severity":
"medium",

"target_group":
[
"People from rural areas"
],

"bias_terms":
[
"know less"
],

"safer_text":
"Knowledge and capability should not be inferred from regional background."
}
```

---

# 8. Dataset Usage by Task

| Dataset Column | Detection | Severity | Extraction | Mitigation |
|----------------|-----------|-----------|------------|------------|
| text | YES | YES | YES | YES |
| label | YES | OPTIONAL | NO | NO |
| bias_terms | NO | NO | YES | NO |
| target_group | NO | NO | YES | NO |
| severity | NO | YES | NO | NO |
| safer_text | NO | NO | NO | YES |

---

# 9. Training Order

Stage 1

Bias Detection

↓

Stage 2

Severity Prediction

↓

Stage 3

Span Extraction

↓

Stage 4

Mitigation Generation

↓

Stage 5

End-to-End Integration

---

# 10. Final System Components

Module A:

Bias Classifier

Module B:

Severity Estimator

Module C:

Bias Extractor

Module D:

Mitigation Generator

Module E:

End-to-End Inference Pipeline

---

End of Task Definition