import re
import unicodedata
from typing import List
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt', quiet=True)
from nltk.corpus import stopwords

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

stemmer = PorterStemmer()
STOPWORDS = set(stopwords.words("english"))
def normalize(text: str, *, lowercase: bool=True, strip_accents: bool=True) -> str:
    s = (text.replace("—", "-").replace("–", "-")
             .replace("“", '"').replace("”", '"')
             .replace("‘", "'").replace("’", "'"))
    if lowercase:
        s = s.casefold()
    if strip_accents:
        s = "".join(ch for ch in unicodedata.normalize("NFD", s)
                    if unicodedata.category(ch) != "Mn")
    return s

def tokenize(text: str) -> List[str]:
    s = normalize(text)
    tokens = word_tokenize(s)
    return [stemmer.stem(tok) for tok in tokens if tok.isalpha() and tok not in STOPWORDS]
