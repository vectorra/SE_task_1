
import json, re
from typing import Dict, List, Set, Iterable, Tuple

def load_index(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def vocabulary(index: Dict) -> List[str]:
    return list(index.get("terms", {}).keys())

def get_postings(index: Dict, term: str) -> Dict[str, Dict]:
    return index.get("terms", {}).get(term, {}).get("documents", {})

def doc_ids_from_postings(postings: Dict[str, Dict]) -> Set[str]:
    return set(postings.keys())

def intersect(a: Set[str], b: Set[str]) -> Set[str]:
    return a & b

def union(a: Set[str], b: Set[str]) -> Set[str]:
    return a | b

def difference(a: Set[str], b: Set[str]) -> Set[str]:
    return a - b

def phrase_search(index: Dict, phrase: str) -> Set[str]:
    terms = phrase.strip().split()
    if not terms:
        return set()
    postings_list = [get_postings(index, t) for t in terms]
    doc_sets = [doc_ids_from_postings(p) for p in postings_list]
    candidates = set.intersection(*doc_sets) if doc_sets else set()
    hits = set()
    for d in candidates:
        pos_lists = [postings_list[i][d]["positions"] for i in range(len(terms))]
        i = j = k = 0
        start_positions = set(pos_lists[0])
        for offset, positions in enumerate(pos_lists[1:], start=1):
            needed = {p + offset for p in start_positions}
            start_positions = needed.intersection(positions)
            if not start_positions:
                break
        if start_positions:
            hits.add(d)
    return hits

def wildcard_search(index: Dict, pattern: str) -> Set[str]:
    regex = '^' + re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.') + '$'
    rx = re.compile(regex)
    docs: Set[str] = set()
    for term in index.get("terms", {}):
        if rx.match(term):
            docs |= doc_ids_from_postings(get_postings(index, term))
    return docs

TOKEN_RE = re.compile(r'"[^"]+"|\(|\)|\bAND\b|\bOR\b|\bNOT\b|[^\s()]+', re.IGNORECASE)

def _eval_token(index: Dict, tok: str) -> Set[str]:
    if tok.startswith('"') and tok.endswith('"'):
        phrase = tok[1:-1]
        return phrase_search(index, phrase)
    elif tok.upper() in ("AND", "OR", "NOT", "(", ")"):
        raise ValueError("Operator/paren must be handled in parser")
    else:
        return doc_ids_from_postings(get_postings(index, tok))

def boolean_search(index: Dict, query: str) -> Set[str]:
    prec = {"NOT": 3, "AND": 2, "OR": 1}
    right_assoc = {"NOT"}
    output: List[str] = []
    ops: List[str] = []
    tokens = TOKEN_RE.findall(query)
    for t in tokens:
        T = t.upper()
        if T in ("AND", "OR", "NOT"):
            while ops:
                top = ops[-1]
                if top in ("AND", "OR", "NOT") and (
                    (top not in right_assoc and prec[top] >= prec[T]) or
                    (top in right_assoc and prec[top] > prec[T])
                ):
                    output.append(ops.pop())
                else:
                    break
            ops.append(T)
        elif t == "(":
            ops.append(t)
        elif t == ")":
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if not ops or ops[-1] != "(":
                raise ValueError("Mismatched parentheses")
            ops.pop() 
        else:
            output.append(t)
    while ops:
        op = ops.pop()
        if op in ("(", ")"):
            raise ValueError("Mismatched parentheses")
        output.append(op)

    stack: List[Set[str]] = []
    for tok in output:
        T = tok.upper()
        if T == "NOT":
            a = stack.pop() if stack else set()
            all_docs = set()
            for term in index.get("terms", {}).values():
                all_docs |= set(term["documents"].keys())
            stack.append(all_docs - a)
        elif T in ("AND", "OR"):
            b = stack.pop() if stack else set()
            a = stack.pop() if stack else set()
            stack.append(a & b if T == "AND" else a | b)
        else:
            stack.append(_eval_token(index, tok))
    return stack[-1] if stack else set()
