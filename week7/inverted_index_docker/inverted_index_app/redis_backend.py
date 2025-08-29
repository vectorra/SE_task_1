import json, re
from typing import Dict, List, Set, Iterable
import redis
from .textutils import tokenize

def get_redis(url: str = "redis://localhost:6379/0") -> redis.Redis:
    return redis.from_url(url, decode_responses=True)

def k_terms() -> str: return "idx:terms"
def k_docs() -> str:  return "idx:docs"
def k_post(term: str) -> str: return f"idx:post:{term}"
def k_doc_terms(doc_id: str) -> str: return f"idx:doc:terms:{doc_id}"

def _json_dumps(obj) -> str:
    return json.dumps(obj, separators=(",", ":"))

def _json_loads(s: str):
    return json.loads(s)

def add_document(r: redis.Redis, doc_id: str, text: str) -> None:
    tokens = tokenize(text)
    pos_map: Dict[str, List[int]] = {}
    for i, t in enumerate(tokens):
        pos_map.setdefault(t, []).append(i)

    pipe = r.pipeline()
    pipe.sadd(k_docs(), doc_id)
    for term, positions in pos_map.items():
        pipe.sadd(k_terms(), term)
        pipe.hset(k_post(term), doc_id, _json_dumps(positions))
        pipe.hset(k_doc_terms(doc_id), term, _json_dumps(positions))
    pipe.execute()

def remove_document(r: redis.Redis, doc_id: str) -> None:
    terms_positions = r.hgetall(k_doc_terms(doc_id))
    if not terms_positions:
        r.srem(k_docs(), doc_id)
        r.delete(k_doc_terms(doc_id))
        return
    pipe = r.pipeline()
    for term in terms_positions.keys():
        pipe.hdel(k_post(term), doc_id)
    pipe.srem(k_docs(), doc_id)
    pipe.delete(k_doc_terms(doc_id))
    pipe.execute()

def _docset_for_term(r: redis.Redis, term: str) -> Set[str]:
    return set(r.hkeys(k_post(term)))

def _intersect_many(sets: List[Set[str]]) -> Set[str]:
    return set.intersection(*sets) if sets else set()

def _union_many(sets: List[Set[str]]) -> Set[str]:
    out: Set[str] = set()
    for s in sets: out |= s
    return out

def _phrase_docs(r: redis.Redis, terms: List[str]) -> Set[str]:
    if not terms: return set()
    postings = [k_post(t) for t in terms]
    doc_sets = [_docset_for_term(r, t) for t in terms]
    candidates = _intersect_many(doc_sets)
    hits: Set[str] = set()
    for d in candidates:
        pos_lists = []
        for t in terms:
            js = r.hget(k_post(t), d)
            pos_lists.append(_json_loads(js))
        start_positions = set(pos_lists[0])
        for offset, plist in enumerate(pos_lists[1:], start=1):
            needed = {p + offset for p in start_positions}
            start_positions = needed.intersection(plist)
            if not start_positions:
                break
        if start_positions:
            hits.add(d)
    return hits

def _pattern_to_regex(glob: str) -> re.Pattern:
    return re.compile("^" + re.escape(glob).replace("\\*", ".*").replace("\\?", ".") + "$")

def wildcard_search(r: redis.Redis, pattern: str) -> Set[str]:
    rx = _pattern_to_regex(pattern)
    docs: Set[str] = set()
    cursor = 0
    while True:
        cursor, members = r.sscan(k_terms(), cursor, count=1000)
        for term in members:
            if rx.match(term):
                docs |= _docset_for_term(r, term)
        if cursor == 0:
            break
    return docs

_TOKEN_RE = re.compile(r'"[^"]+"|\(|\)|\bAND\b|\bOR\b|\bNOT\b|[^\s()]+', re.IGNORECASE)

def _eval_leaf(r: redis.Redis, tok: str) -> Set[str]:
    if tok.startswith('"') and tok.endswith('"'):
        phrase = tok[1:-1]
        terms = phrase.strip().split()
        return _phrase_docs(r, terms)
    else:
        return _docset_for_term(r, tok)

def boolean_search(r: redis.Redis, query: str) -> Set[str]:
    prec = {"NOT": 3, "AND": 2, "OR": 1}
    right_assoc = {"NOT"}
    output: List[str] = []
    ops: List[str] = []
    tokens = _TOKEN_RE.findall(query)

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
    all_docs = set(get_all_docs(r))
    for tok in output:
        T = tok.upper()
        if T == "NOT":
            a = stack.pop() if stack else set()
            stack.append(all_docs - a)
        elif T in ("AND", "OR"):
            b = stack.pop() if stack else set()
            a = stack.pop() if stack else set()
            stack.append(a & b if T == "AND" else a | b)
        else:
            stack.append(_eval_leaf(r, tok))
    return stack[-1] if stack else set()

def get_all_docs(r: redis.Redis) -> Iterable[str]:
    cursor = 0
    while True:
        cursor, members = r.sscan(k_docs(), cursor, count=1000)
        for d in members:
            yield d
        if cursor == 0:
            break

def load_index_json_to_redis(r: redis.Redis, index_path: str) -> None:
    idx = json.load(open(index_path, "r", encoding="utf-8"))
    terms = idx.get("terms", {})
    pipe = r.pipeline()
    for term, entry in terms.items():
        pipe.sadd(k_terms(), term)
        post_key = k_post(term)
        for doc_id, payload in entry["documents"].items():
            positions = payload["positions"]
            pipe.sadd(k_docs(), doc_id)
            pipe.hset(post_key, doc_id, _json_dumps(positions))
            pipe.hset(k_doc_terms(doc_id), term, _json_dumps(positions))
    pipe.execute()
