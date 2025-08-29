from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import json
from pathlib import Path
from .textutils import tokenize

@dataclass
class Posting:
    tf: int = 0
    positions: List[int] = field(default_factory=list)

@dataclass
class TermEntry:
    document_frequency: int = 0
    total_frequency: int = 0
    documents: Dict[str, Posting] = field(default_factory=dict)

    def add(self, doc_id: str, positions: List[int]):
        if not positions:
            return
        p = self.documents.get(doc_id)
        if p is None:
            p = Posting()
            self.documents[doc_id] = p
            self.document_frequency += 1
        p.tf += len(positions)
        p.positions.extend(positions)
        self.total_frequency += len(positions)

class InvertedIndex:
    def __init__(self):
        self.terms: Dict[str, TermEntry] = {}
        self.doc_count = 0
        self.total_tokens = 0

    def index_document(self, doc_id: str, text: str):
        tokens = tokenize(text)
        self.total_tokens += len(tokens)
        self.doc_count += 1
        positions_by_term: Dict[str, List[int]] = {}
        for i, tok in enumerate(tokens):
            positions_by_term.setdefault(tok, []).append(i)
        for term, pos_list in positions_by_term.items():
            entry = self.terms.get(term)
            if entry is None:
                entry = TermEntry()
                self.terms[term] = entry
            entry.add(doc_id, pos_list)

    def to_dict(self) -> Dict:
        out = {"terms": {}, "meta": {"documents": self.doc_count, "tokens": self.total_tokens}}
        for t, entry in self.terms.items():
            docs_obj = {}
            for d, p in entry.documents.items():
                docs_obj[d] = {"frequency": int(p.tf), "positions": sorted(int(x) for x in p.positions)}
            out["terms"][t] = {
                "document_frequency": int(entry.document_frequency),
                "total_frequency": int(entry.total_frequency),
                "documents": docs_obj,
            }
        return out

    def save_json(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

def build_from_json_docs(
    input_json_path: str | Path,
    *,
    id_key: str = "id",
    text_key: str = "content",
) -> InvertedIndex:
    import json
    from pathlib import Path
    idx = InvertedIndex()
    data = json.load(open(input_json_path, "r", encoding="utf-8"))
    for item in data:
        doc_id = str(item[id_key])
        text = str(item[text_key])
        idx.index_document(doc_id, text)
    return idx
