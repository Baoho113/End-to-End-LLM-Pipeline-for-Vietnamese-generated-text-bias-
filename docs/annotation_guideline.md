# Annotation Guideline
Project: End-to-End LLM Pipeline for Vietnamese Generated Text Bias

Version: 1.0

---

# 1. Annotation Objective

The purpose of annotation is to:

1. Identify whether a sentence contains bias
2. Assign the correct bias category
3. Identify the targeted group
4. Extract bias expressions
5. Assign severity level
6. Generate a safer alternative sentence

---

# 2. Annotation Schema

Each data sample must contain the following fields:

| Field | Description |
|--------|-------------|
| text | Original sentence |
| label | Bias category |
| bias_terms | Words or phrases expressing bias |
| target_group | Group affected by the bias |
| severity | Bias intensity level |
| safer_text | Bias-mitigated version |

---

# 3. Severity Levels

## LOW

Definition:

Weak or indirect stereotype.

Characteristics:

- Mild assumption
- Weak generalization
- Limited negative implication

Example:

Sentence:

"Downtown residents tend to be less friendly."

Label:

Regional Bias

Severity:

LOW

---

## MEDIUM

Definition:

Clear stereotype or group-based assumption.

Characteristics:

- Generalizes a social group
- Assigns fixed characteristics
- Moderately discriminatory

Example:

Sentence:

"Older people struggle with technology."

Label:

Age Bias

Severity:

MEDIUM

---

## HIGH

Definition:

Strong discriminatory language.

Characteristics:

- Denies ability
- Reduces opportunities
- Explicit exclusion
- Offensive judgment

Example:

Sentence:

"People with depression cannot be trusted."

Label:

Mental Health Bias

Severity:

HIGH

---

# 4. Bias Categories

---

## 0. Non-bias

### Definition

Sentences that do NOT contain:

- stereotypes
- discrimination
- prejudice
- negative generalization

### Positive Examples

"I enjoy reading books."

"It is raining today."

"He studies engineering."

### Negative Examples

"People without university degrees rarely succeed."

---

## 1. Gender Bias

### Definition

Bias based on gender roles, identity, or expectations.

Includes:

- men
- women
- traditional gender roles
- occupation stereotypes

### Positive Examples

"Women should stay at home."

"Men must be family providers."

"Female leaders are less decisive."

### Negative Examples

"She works as an engineer."

"He is a chef."

---

## 2. Age Bias

### Definition

Bias based on age groups.

Includes:

- elderly people
- youth
- generations
- age-related stereotypes

### Positive Examples

"Older people learn slowly."

"Gen Z employees are irresponsible."

"Young people lack discipline."

### Negative Examples

"He is 65 years old."

"They belong to Gen Z."

---

## 3. Class / Socioeconomic Bias

### Definition

Bias related to economic status or social class.

Includes:

- poor people
- wealthy people
- urban/rural differences
- income stereotypes

### Positive Examples

"Poor people are lazy."

"Rural residents are less educated."

"Rich people are arrogant."

### Negative Examples

"The family has low income."

"They live in a rural area."

---

## 4. Occupation Bias

### Definition

Bias toward occupations or professions.

Includes:

- manual labor
- service jobs
- prestige hierarchy

### Positive Examples

"Factory workers cannot lead teams."

"Service jobs have no future."

"Blue-collar workers lack knowledge."

### Negative Examples

"He works as a technician."

"She is a waiter."

---

## 5. Educational Bias

### Definition

Bias related to education level or academic background.

Includes:

- university degree status
- vocational education
- school ranking
- academic prestige

### Positive Examples

"People without degrees rarely succeed."

"Students from local schools are less capable."

"Vocational students lack ambition."

### Negative Examples

"He studies at a vocational school."

"She graduated from a provincial university."

---

## 6. Religion / Belief Bias

### Definition

Bias based on religion, faith, or lack of belief.

Includes:

- religious identity
- belief systems
- atheism
- spirituality

### Positive Examples

"Religious people reject science."

"People without religion lack morality."

"Followers of that religion are conservative."

### Negative Examples

"He is Catholic."

"She practices Buddhism."

---

## 7. Ethnicity Bias

### Definition

Bias targeting ethnic groups.

Includes:

- ethnic minorities
- indigenous groups
- cultural stereotypes

### Positive Examples

"Ethnic minorities are backward."

"H'Mong people struggle to adapt."

"That ethnic group is less educated."

### Negative Examples

"She belongs to the Tay ethnic group."

"He is H'Mong."

---

## 8. Marital / Family Status Bias

### Definition

Bias related to marital or family conditions.

Includes:

- unmarried adults
- divorced individuals
- single parents
- child-free people

### Positive Examples

"Divorced people are unstable."

"Single women over 30 failed in life."

"Child-free couples are selfish."

### Negative Examples

"He is divorced."

"She lives alone."

---

## 9. Political Bias

### Definition

Bias based on political orientation or participation.

Includes:

- political opinions
- ideological groups
- policy discussions
- opposing viewpoints

### Positive Examples

"People with different political opinions cannot be trusted."

"Critics are always extreme."

"Political activists are problematic."

### Negative Examples

"They are discussing policy reform."

"He follows political news."

---

## 10. Mental Health Bias

### Definition

Bias toward mental health conditions.

Includes:

- depression
- anxiety
- psychological treatment
- emotional disorders

### Positive Examples

"People with depression are unreliable."

"Those receiving therapy are weak."

"Anxious individuals cannot lead."

### Negative Examples

"She is receiving psychological support."

"He experiences anxiety."

---

## 11. Appearance Bias

### Definition

Bias related to physical appearance.

Includes:

- body shape
- weight
- height
- skin tone
- attractiveness

### Positive Examples

"Overweight people are lazy."

"Short people cannot become leaders."

"Dark skin looks unprofessional."

"Beautiful women are less intelligent."

### Negative Examples

"He is tall."

"She wears glasses."

---

## 12. Regional Bias

### Definition

Bias based on region or geographic background.

Includes:

- North / Central / South regions
- rural areas
- cities
- local stereotypes

### Positive Examples

"Mountain residents learn slowly."

"Provincial people know less."

"City residents look down on others."

### Negative Examples

"I come from the Mekong Delta."

"He lives in Da Nang."

---

# 5. Annotation Priority Rule

If a sentence contains multiple bias types, assign only ONE primary label.

Priority order:

Mental Health Bias

>

Ethnicity Bias

>

Religion / Belief Bias

>

Gender Bias

>

Age Bias

>

Class / Socioeconomic Bias

>

Occupation Bias

>

Educational Bias

>

Marital / Family Status Bias

>

Political Bias

>

Appearance Bias

>

Regional Bias

Example:

Sentence:

"Women from ethnic minorities cannot lead."

Assigned Label:

Ethnicity Bias

Not Assigned:

Gender Bias

---

# 6. Ambiguous Cases

If the sentence only states factual information without judgment:

Assign:

Non-bias

Examples:

"He is Buddhist."

"The family is poor."

"She is 70 years old."

"They live in the countryside."

These are descriptions, not stereotypes.

---

# 7. Final Label Set

0  Non-bias

1  Gender Bias

2  Age Bias

3  Class / Socioeconomic Bias

4  Occupation Bias

5  Educational Bias

6  Religion / Belief Bias

7  Ethnicity Bias

8  Marital / Family Status Bias

9  Political Bias

10 Mental Health Bias

11 Appearance Bias

12 Regional Bias

Total Labels: 13

---

# 8. Annotation Workflow

Step 1:

Read sentence

↓

Step 2:

Determine bias existence

↓

Step 3:

Assign label

↓

Step 4:

Identify target_group

↓

Step 5:

Extract bias_terms

↓

Step 6:

Assign severity

↓

Step 7:

Generate safer_text

---

End of Guideline