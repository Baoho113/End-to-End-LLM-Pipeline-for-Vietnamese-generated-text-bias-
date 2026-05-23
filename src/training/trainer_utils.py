import pandas as pd

from datasets import Dataset

from transformers import (
AutoTokenizer
)

from config import MODEL_NAME

tokenizer = AutoTokenizer.from_pretrained(
MODEL_NAME
)

def load_csv(
path
):

    df = pd.read_csv(
        path
    )

    return Dataset.from_pandas(
        df
    )

def tokenize(
batch
):

    return tokenizer(

        batch[
        "text"
        ],

        padding="max_length",

        truncation=True,

        max_length=128

    )