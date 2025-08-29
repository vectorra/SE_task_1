Inverted Index (JSON + Redis) — CLI & Docker
Tiny search toolkit that:
    parses a JSON corpus ([{ "id": "...", "content": "..." }, ...]),
    builds a positional inverted index,
    runs Boolean / Phrase / Wildcard queries,
    optional Redis backend for shared, real-time updates.
How it works (short)
    Index build: tokenize → term → {doc → positions, freq}, plus df/tf.
    Boolean: set ops over postings (AND/OR/NOT, parentheses, quoted phrases).
    Phrase: intersect candidates, verify adjacent positions.
    Wildcard: glob→regex over vocabulary, then union postings.
Redis mode: same logic with postings in Redis; supports add/remove docs live.
    Multiprocessing
    Build:
        build → single process
        mr-build → multi-process (mappers/reducers)
    Queries: single process per run; scale by running multiple workers (or via Redis).
Docker quick start
    # start redis (optional)
        cker compose up -d --build redis
         Build (single process)
            # writes ./data/index.json
                docker compose run --rm indexer build \
                --input /data/documents.json \
                --output /data/index.json \
                --id id --text content
         Build (parallel, recommended on macOS: keep tmp on container disk)
            #writes final index to /segments; intermediates in /tmp (fast)
                docker compose run --rm indexer mr-build \
                --input /data/documents.json \
                --output /data/index.json \
                --id id --text content \
                --mappers 14 --reducers 14 \
                --tmpdir /tmp
Query (file index)
    # Boolean
        docker compose run --rm indexer search \
        --index /segments/index.json \
        --query 'protein AND ("contact map" OR alignment) NOT toy'

    # Phrase
        docker compose run --rm indexer phrase \
        --index /segments/index.json \
        --phrase "contact map"

    # Wildcard
        docker compose run --rm indexer wildcard \
        --index /segments/index.json \
        --pattern "cont*"
    Redis (optional)
    # push file index into redis
        docker compose run --rm indexer redis-push \
        --index /segments/index.json \
        --redis redis://redis:6379/0

    # boolean / wildcard against redis
        docker compose run --rm indexer redis-search   --query 'protein AND alignment' --redis redis://redis:6379/0
        docker compose run --rm indexer redis-wildcard --pattern 'cont*'               --redis redis://redis:6379/0

    # real-time updates
        docker compose run --rm indexer redis-add-doc    --doc-id doc_new --text "..." --redis redis://redis:6379/0
        docker compose run --rm indexer redis-remove-doc --doc-id doc_new               --redis redis://redis:6379/0
Benchmarks (example, your run)
    Build:
        1 proc: 5.87s (≈358k tokens/s)
        MR 14×14: 5.29s
        MR 14×14 + --tmpdir /tmp: 4.67s
    Queries (inverted vs linear):
        Boolean "data AND science": 0.01 ms vs ~1.44 s
        Phrase "machine learning": 0.02 ms vs ~1.49 s
        Wildcard comput*: ~2.8 ms (linear n/a)