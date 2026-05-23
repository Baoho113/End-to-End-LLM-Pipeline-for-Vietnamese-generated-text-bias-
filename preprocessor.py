"""
preprocessor.py — Vietnamese text normalisation and tokenisation.

Steps:
  1. Unicode NFC normalisation (consistent diacritics)
  2. Lowercasing
  3. Strip URLs, emails, excessive punctuation
  4. Vietnamese word segmentation (underthesea)
  5. Optional stopword removal
"""

import re
import unicodedata

try:
    from underthesea import word_tokenize as vn_tokenize
    HAS_UNDERTHESEA = True
except ImportError:
    HAS_UNDERTHESEA = False
    def vn_tokenize(text):
        return text.split()


class Preprocessor:
    """Normalises and tokenises Vietnamese text."""

    STOP_WORDS = {
        "và", "của", "là", "có", "cho", "với", "được", "này", "đó",
        "các", "một", "những", "trong", "đã", "sẽ", "để", "từ",
        "khi", "nếu", "nhưng", "hay", "hoặc", "thì", "mà", "bị",
        "vì", "do", "tại", "về", "ra", "lên", "lại", "đi", "vào",
        "rồi", "nên", "cũng", "rất", "quá", "hơn", "nhất",
    }

    # Regex pattern to keep Vietnamese characters plus basic punctuation
    CLEAN_PATTERN = re.compile(
        r"[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộ"
        r"ơớờởỡợùúủũụưứừửữựỳýỷỹỵđ.,!?;:\-]",
        re.IGNORECASE,
    )

    def __init__(self, remove_stopwords: bool = False):
        self.remove_stopwords = remove_stopwords

    def normalize_unicode(self, text: str) -> str:
        """NFC normalisation — critical for Vietnamese diacritics."""
        return unicodedata.normalize("NFC", text)

    def clean_text(self, text: str) -> str:
        """Remove URLs, emails, excessive whitespace."""
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"\S+@\S+\.\S+", "", text)
        text = self.CLEAN_PATTERN.sub(" ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> str:
        """Vietnamese word segmentation."""
        tokens = vn_tokenize(text)
        if self.remove_stopwords:
            tokens = [t for t in tokens if t.lower() not in self.STOP_WORDS]
        return " ".join(tokens)

    def process(self, text: str) -> str:
        """Full preprocessing pipeline for a single text."""
        text = self.normalize_unicode(text)
        text = text.lower()
        text = self.clean_text(text)
        text = self.tokenize(text)
        return text

    def process_batch(self, texts: list[str]) -> list[str]:
        """Process a list of texts."""
        return [self.process(t) for t in texts]
