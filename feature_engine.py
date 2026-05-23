"""
feature_engine.py — Text-to-features conversion.

Current implementation: TF-IDF with word + character n-grams.
Designed as a drop-in replaceable module. To use PhoBERT instead,
create a new class with the same fit/transform/fit_transform interface.
"""

from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer

from config import (
    TFIDF_WORD_MAX_FEATURES, TFIDF_CHAR_MAX_FEATURES,
    TFIDF_WORD_NGRAM, TFIDF_CHAR_NGRAM,
    TFIDF_MIN_DF, TFIDF_MAX_DF,
)


class TfidfFeatureEngine:
    """
    TF-IDF feature extraction with word + character n-grams.

    Character n-grams (2-5) capture morphological patterns in
    Vietnamese like "lạc_hậu" and "kém_văn_minh" that are
    strong bias signals.

    Interface:
      .fit(texts)           — learn vocabulary
      .transform(texts)     — vectorise new texts
      .fit_transform(texts) — both
    """

    def __init__(self):
        self.word_vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=TFIDF_WORD_NGRAM,
            max_features=TFIDF_WORD_MAX_FEATURES,
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            sublinear_tf=True,
        )
        self.char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=TFIDF_CHAR_NGRAM,
            max_features=TFIDF_CHAR_MAX_FEATURES,
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            sublinear_tf=True,
        )

    def fit(self, texts):
        self.word_vectorizer.fit(texts)
        self.char_vectorizer.fit(texts)
        return self

    def transform(self, texts):
        word_feats = self.word_vectorizer.transform(texts)
        char_feats = self.char_vectorizer.transform(texts)
        return hstack([word_feats, char_feats])

    def fit_transform(self, texts):
        self.fit(texts)
        return self.transform(texts)

    @property
    def feature_names(self):
        return (
            self.word_vectorizer.get_feature_names_out().tolist()
            + self.char_vectorizer.get_feature_names_out().tolist()
        )
