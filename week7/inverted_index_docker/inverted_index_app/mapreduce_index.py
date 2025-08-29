import json, math, gzip
from pathlib import Path
from typing import Dict, List, Iterable, Tuple
import multiprocessing as mp
from .textutils import tokenize

def _is_jsonl(path: Path) -> bool:
    s = str(path).lower()
    return s.endswith(".jsonl") or s.endswith(".jsonl.gz")

def _open_text(path: Path, mode: str="rt"):
    if str(path).lower().endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")

def _iter_docs(input_path: Path, id_key: str, text_key: str) -> Iterable[Tuple[str, str]]:
    if _is_jsonl(input_path):
        with _open_text(input_path) as f:
            for line in f:
                line = line.strip()
                if not line: continue
                obj = json.loads(line)
                yield str(obj[id_key]), str(obj[text_key])
    else:
        data = json.load(open(input_path, "r", encoding="utf-8"))
        for obj in data:
            yield str(obj[id_key]), str(obj[text_key])

def _hash_part(term: str, reducers: int) -> int:
    return (hash(term) & 0x7fffffff) % reducers

def _mapper_worker(args):
    mapper_id, docs_slice, reducers, tmpdir = args
    tmpdir = Path(tmpdir)
    writers = [open(tmpdir / f"part-m{mapper_id}-r{r}.jsonl", "w", encoding="utf-8")
               for r in range(reducers)]
    emitted = 0
    for doc_id, text in docs_slice:
        pos_by_term: Dict[str, List[int]] = {}
        for i, tok in enumerate(tokenize(text)):
            pos_by_term.setdefault(tok, []).append(i)
        for term, pos in pos_by_term.items():
            r = _hash_part(term, reducers)
            writers[r].write(json.dumps({"t": term, "d": doc_id, "p": pos}, ensure_ascii=False) + "\n")
            emitted += 1
    for w in writers: w.close()
    return emitted

def _reducer_worker(args):
    r_id, mapper_count, tmpdir = args
    tmpdir = Path(tmpdir)
    shard_terms: Dict[str, Dict[str, Dict[str, object]]] = {}
    docs_seen = set()
    total_tokens = 0

    for m in range(mapper_count):
        p = tmpdir / f"part-m{m}-r{r_id}.jsonl"
        if not p.exists(): continue
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                term, doc, positions = rec["t"], rec["d"], rec["p"]
                docs_seen.add(doc)
                total_tokens += len(positions)
                docmap = shard_terms.setdefault(term, {})
                d = docmap.setdefault(doc, {"frequency": 0, "positions": []})
                d["frequency"] += len(positions)
                d["positions"].extend(positions)


    for term, docmap in shard_terms.items():
        for doc, payload in docmap.items():
            payload["positions"] = sorted(int(x) for x in payload["positions"])

    shard = {
        "terms": {
            term: {
                "document_frequency": len(docmap),
                "total_frequency": sum(v["frequency"] for v in docmap.values()),
                "documents": docmap,
            } for term, docmap in shard_terms.items()
        },
        "meta": {"docs_in_shard": len(docs_seen), "tokens_in_shard": total_tokens}
    }
    out = tmpdir / f"shard-r{r_id}.json"
    json.dump(shard, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    return str(out)

def mr_build(
    input_path: str,
    output_path: str,
    *,
    id_key: str = "id",
    text_key: str = "content",
    mappers: int = 4,
    reducers: int = 4,
    tmpdir: str | None = None,
) -> Dict:
    input_path = Path(input_path)
    output_path = Path(output_path)
    tmp = Path(tmpdir or (output_path.parent / "segments"))
    tmp.mkdir(parents=True, exist_ok=True)

    docs = list(_iter_docs(input_path, id_key, text_key))
    n = len(docs)
    if n == 0:
        idx = {"terms": {}, "meta": {"documents": 0, "tokens": 0}}
        json.dump(idx, open(output_path, "w", encoding="utf-8"))
        return idx


    mappers = max(1, mappers)
    reducers = max(1, reducers)
    step = math.ceil(n / mappers)
    mapper_jobs = [(m, docs[m*step:min(n,(m+1)*step)], reducers, str(tmp)) for m in range(mappers)]
    with mp.Pool(processes=mappers) as pool:
        for _ in pool.imap_unordered(_mapper_worker, mapper_jobs):
            pass

 
    reducer_jobs = [(r, mappers, str(tmp)) for r in range(reducers)]
    shard_paths = []
    with mp.Pool(processes=reducers) as pool:
        for sp in pool.imap_unordered(_reducer_worker, reducer_jobs):
            shard_paths.append(sp)

    final_terms: Dict[str, Dict] = {}
    total_tokens = 0
    doc_ids = set()
    for sp in shard_paths:
        shard = json.load(open(sp, "r", encoding="utf-8"))
        for term, entry in shard["terms"].items():
            dst = final_terms.setdefault(term, {"document_frequency": 0, "total_frequency": 0, "documents": {}})
            dst["total_frequency"] += entry["total_frequency"]
            for doc, payload in entry["documents"].items():
                doc_ids.add(doc)
                d = dst["documents"].setdefault(doc, {"frequency": 0, "positions": []})
                d["frequency"] += payload["frequency"]
                d["positions"].extend(payload["positions"])
            dst["document_frequency"] = len(dst["documents"])
        total_tokens += shard["meta"]["tokens_in_shard"]

    for term, entry in final_terms.items():
        for doc, payload in entry["documents"].items():
            payload["positions"] = sorted(int(x) for x in payload["positions"])

    idx = {"terms": final_terms, "meta": {"documents": len(doc_ids), "tokens": total_tokens}}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(idx, open(output_path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    return idx
