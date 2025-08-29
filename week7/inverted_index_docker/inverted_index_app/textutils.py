import re
import unicodedata
from typing import List
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")

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
    return word_tokenize(s)
