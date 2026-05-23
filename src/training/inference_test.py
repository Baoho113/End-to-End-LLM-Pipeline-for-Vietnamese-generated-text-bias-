import torch

from transformers import (

AutoTokenizer,

AutoModelForSequenceClassification

)

tokenizer = (
AutoTokenizer.from_pretrained(

"checkpoints/phobert_bias_classifier"

)
)

model = (
AutoModelForSequenceClassification
.from_pretrained(

"checkpoints/phobert_bias_classifier"

)
)

text = "Người già thường khó tiếp thu."

inputs = tokenizer(

text,

return_tensors="pt",

padding=True,

truncation=True

)

with torch.no_grad():

    output = model(
        **inputs
    )

pred = output.logits.argmax(
dim=1
)

print(pred)