import numpy as np

from transformers import (

AutoModelForSequenceClassification,

TrainingArguments,

Trainer

)

from trainer_utils import (

load_csv,

tokenize

)

from metrics import (
compute_metrics
)

from config import *

train_ds = load_csv(
TRAIN_PATH
)

val_ds = load_csv(
VAL_PATH
)

train_ds = train_ds.map(
tokenize,
batched=True
)

val_ds = val_ds.map(
tokenize,
batched=True
)

train_ds = train_ds.rename_column(
"label_id",
"labels"
)

val_ds = val_ds.rename_column(
"label_id",
"labels"
)
cols_to_remove = []

for col in [

"id",

"text",

"label",

"bias_terms",

"target_group",

"severity",

"safer_text"

]:

    if col in train_ds.column_names:
        cols_to_remove.append(col)

train_ds = train_ds.remove_columns(
cols_to_remove
)

val_ds = val_ds.remove_columns(
[
c for c in cols_to_remove
if c in val_ds.column_names
]
)

train_ds.set_format(
type="torch",
columns=[
"input_ids",
"attention_mask",
"labels"
]
)

val_ds.set_format(
type="torch",
columns=[
"input_ids",
"attention_mask",
"labels"
]
)

model = (
AutoModelForSequenceClassification
.from_pretrained(

MODEL_NAME,

num_labels=NUM_LABELS

)
)

args = TrainingArguments(

output_dir=OUTPUT_DIR,

eval_strategy="epoch",

save_strategy="epoch",

learning_rate=LEARNING_RATE,

per_device_train_batch_size=BATCH_SIZE,

per_device_eval_batch_size=BATCH_SIZE,

num_train_epochs=EPOCHS,

weight_decay=0.01,

logging_steps=50,

load_best_model_at_end=True,

metric_for_best_model="macro_f1"

)

trainer = Trainer(

model=model,

args=args,

train_dataset=train_ds,

eval_dataset=val_ds,

compute_metrics=compute_metrics

)

trainer.train()

trainer.save_model(
OUTPUT_DIR
)