# inverted_index_app/cli.py
import argparse, time
from .indexer import build_from_json_docs
from .query import load_index, boolean_search, phrase_search, wildcard_search
from .redis_backend import (
    get_redis, add_document, remove_document,
    boolean_search as redis_boolean_search,
    wildcard_search as redis_wildcard_search,
    load_index_json_to_redis,
)
from .mapreduce_index import mr_build 

def main():
    p = argparse.ArgumentParser(prog="inverted-index")
    sub = p.add_subparsers(dest="cmd", required=True)


    pb = sub.add_parser("build", help="Build inverted index from JSON docs")
    pb.add_argument("--input", required=True)
    pb.add_argument("--output", required=True)
    pb.add_argument("--id", default="id")
    pb.add_argument("--text", default="content")


    pmr = sub.add_parser("mr-build", help="Build index with multi-process map/reduce")
    pmr.add_argument("--input", required=True, help="JSON array or JSONL(.gz)")
    pmr.add_argument("--output", required=True, help="Where to save index.json")
    pmr.add_argument("--id", default="id", help="Key for doc id")
    pmr.add_argument("--text", default="content", help="Key for text")
    pmr.add_argument("--mappers", type=int, default=4)
    pmr.add_argument("--reducers", type=int, default=4)
    pmr.add_argument("--tmpdir", default="/segments", help="Intermediate files dir")


    ps = sub.add_parser("search", help="Boolean search")
    ps.add_argument("--index", required=True)
    ps.add_argument("--query", required=True)

    pp = sub.add_parser("phrase", help='Phrase search "..."')
    pp.add_argument("--index", required=True)
    pp.add_argument("--phrase", required=True)

    pw = sub.add_parser("wildcard", help="Wildcard search with * and ?")
    pw.add_argument("--index", required=True)
    pw.add_argument("--pattern", required=True)


    pr = sub.add_parser("redis-push", help="Load local JSON index into Redis")
    pr.add_argument("--index", required=True)
    pr.add_argument("--redis", default="redis://redis:6379/0")

    prs = sub.add_parser("redis-search", help="Boolean search in Redis")
    prs.add_argument("--query", required=True)
    prs.add_argument("--redis", default="redis://redis:6379/0")

    prw = sub.add_parser("redis-wildcard", help="Wildcard search in Redis")
    prw.add_argument("--pattern", required=True)
    prw.add_argument("--redis", default="redis://redis:6379/0")

    pad = sub.add_parser("redis-add-doc", help="Add a document to Redis index")
    pad.add_argument("--doc-id", required=True)
    pad.add_argument("--text", required=True)
    pad.add_argument("--redis", default="redis://redis:6379/0")

    prd = sub.add_parser("redis-remove-doc", help="Remove a document from Redis index")
    prd.add_argument("--doc-id", required=True)
    prd.add_argument("--redis", default="redis://redis:6379/0")

    args = p.parse_args()

    if args.cmd == "build":
        t0 = time.perf_counter()
        idx = build_from_json_docs(args.input, id_key=args.id, text_key=args.text)
        idx.save_json(args.output)
        dt = time.perf_counter() - t0
        toks = idx.total_tokens
        print(f"Indexed {idx.doc_count} docs, {toks} tokens → {args.output}")
        print(f"Build time: {dt:.3f}s ({toks/dt:,.0f} tokens/s, {idx.doc_count/dt:,.1f} docs/s)")

    elif args.cmd == "mr-build":
        t0 = time.perf_counter()
        idx = mr_build(
            args.input, args.output,
            id_key=args.id, text_key=args.text,
            mappers=args.mappers, reducers=args.reducers,
            tmpdir=args.tmpdir,
        )
        dt = time.perf_counter() - t0
        print(f"MR build: docs={idx['meta']['documents']} tokens={idx['meta']['tokens']} "
              f"mappers={args.mappers} reducers={args.reducers} time={dt:.3f}s → {args.output}")

    elif args.cmd == "search":
        index = load_index(args.index)
        hits = boolean_search(index, args.query)
        print("\n".join(sorted(hits)))

    elif args.cmd == "phrase":
        index = load_index(args.index)
        hits = phrase_search(index, args.phrase)
        print("\n".join(sorted(hits)))

    elif args.cmd == "wildcard":
        index = load_index(args.index)
        hits = wildcard_search(index, args.pattern)
        print("\n".join(sorted(hits)))

    elif args.cmd == "redis-push":
        r = get_redis(args.redis)
        load_index_json_to_redis(r, args.index)
        print("Pushed index to Redis.")

    elif args.cmd == "redis-search":
        r = get_redis(args.redis)
        hits = redis_boolean_search(r, args.query)
        print("\n".join(sorted(hits)) if hits else "(no results)")

    elif args.cmd == "redis-wildcard":
        r = get_redis(args.redis)
        hits = redis_wildcard_search(r, args.pattern)
        print("\n".join(sorted(hits)) if hits else "(no results)")

    elif args.cmd == "redis-add-doc":
        r = get_redis(args.redis)
        add_document(r, args.doc_id, args.text)
        print(f"Added {args.doc_id}")

    elif args.cmd == "redis-remove-doc":
        r = get_redis(args.redis)
        remove_document(r, args.doc_id)
        print(f"Removed {args.doc_id}")

if __name__ == "__main__":
    main()
