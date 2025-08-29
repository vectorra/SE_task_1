import json, time, argparse
from pathlib import Path
from inverted_index_app.indexer import build_from_json_docs
from inverted_index_app.textutils import tokenize

def estimate_tokens(json_path, id_key, text_key, sample_docs=2000):
    data = json.load(open(json_path, "r", encoding="utf-8"))
    n = len(data)
    s = min(sample_docs, n)
    tot = 0
    for i in range(s):
        tot += len(tokenize(str(data[i][text_key])))
    avg = tot / max(1, s)
    return int(avg * n), n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--id", default="id")
    ap.add_argument("--text", default="content")
    args = ap.parse_args()

    est_tokens, n_docs = estimate_tokens(args.input, args.id, args.text)
    print(f"[est] docs={n_docs}  est_tokens={est_tokens:,}")

    t0 = time.perf_counter()
    idx = build_from_json_docs(args.input, id_key=args.id, text_key=args.text)
    build_s = time.perf_counter() - t0
    idx.save_json(args.output)

    toks = idx.total_tokens
    print(f"[build] docs={idx.doc_count} tokens={toks:,} time={build_s:.3f}s  "
          f"throughput={toks/max(1e-9,build_s):.0f} tokens/s "
          f"({idx.doc_count/max(1e-9,build_s):.1f} docs/s)")

if __name__ == "__main__":
    main()
