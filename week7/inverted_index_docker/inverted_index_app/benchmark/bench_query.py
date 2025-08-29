import json, time, statistics as st, argparse
from inverted_index_app.query import load_index, boolean_search, phrase_search, wildcard_search
from inverted_index_app.textutils import tokenize, normalize

def timeit(fn, n=7, warmup=2):
    xs = []
    for _ in range(warmup): fn()
    for _ in range(n): 
        t0 = time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    return {"median_ms": 1000*st.median(xs), "p90_ms": 1000*st.quantiles(xs, n=10)[8], "runs": n}

def linear_boolean_scan(docs, q):
    terms = [w for w in q.replace("AND"," ").replace("OR"," ").replace("NOT"," ").split() if w and w[0]!='"']
    terms = [normalize(t) for t in terms]
    hits = []
    for d in docs:
        text = normalize(d["content"])
        toks = set(tokenize(text))
        if all(t in toks for t in terms):
            hits.append(d["id"])
    return set(hits)

def linear_phrase_scan(docs, phrase):
    words = [normalize(w) for w in phrase.split()]
    hits = []
    for d in docs:
        toks = tokenize(normalize(d["content"]))
        for i in range(0, max(0, len(toks)-len(words)+1)):
            if toks[i:i+len(words)] == words:
                hits.append(d["id"]); break
    return set(hits)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--docs",  required=True) 
    ap.add_argument("--query", action="append", default=[
        'data AND science',
        '"machine learning"',
        'comput*',
    ])
    args = ap.parse_args()

    docs = json.load(open(args.docs, "r", encoding="utf-8"))
    index = load_index(args.index)

    print(f"Loaded: docs={len(docs)} terms={len(index['terms'])}")

    for q in args.query:
        print(f"\n== Query: {q}")
        if q.startswith('"') and q.endswith('"'):
            inv = timeit(lambda: phrase_search(index, q.strip('"')))
            lin = timeit(lambda: linear_phrase_scan(docs, q.strip('"')))
        elif "*" in q or "?" in q:
            inv = timeit(lambda: wildcard_search(index, q))
            lin = {"median_ms": float("nan"), "p90_ms": float("nan"), "runs": 0}
        else:
            inv = timeit(lambda: boolean_search(index, q))
            lin = timeit(lambda: linear_boolean_scan(docs, q))
        print(f"[inverted] median={inv['median_ms']:.2f}ms  p90={inv['p90_ms']:.2f}ms  runs={inv['runs']}")
        if lin["runs"]>0:
            print(f"[linear  ] median={lin['median_ms']:.2f}ms  p90={lin['p90_ms']:.2f}ms  runs={lin['runs']}")
        else:
            print("[linear  ] n/a for wildcard")
    print("\nTip: increase --query ... to benchmark your real workload.")

if __name__ == "__main__":
    main()
