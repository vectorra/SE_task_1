FastAPI Notes API
    Simple Notes API using FastAPI, Postgres, and Redis.
    Supports async database access and caching. Runs in Docker.

Run
    docker-compose up --build
    API → http://localhost:8000
    Docs → http://localhost:8000/docs

Usage
    Create note
        curl -X POST http://localhost:8000/notes/ \
        -H "Content-Type: application/json" \
        -d '{"title": "Hello", "content": "World"}'
    Get notes       
        curl -X GET http://localhost:8000/notes/

Load Test
    With hey:
        hey -n 10000 -c 100 http://localhost:8000/notes/
        Shows requests/sec and latency.

Stack
    FastAPI
    SQLAlchemy (async)
    PostgreSQL
    Redis
    Docker Compose


No Caching 
 
        10000 Request prcessing time with only db read/write with asyncio

        Summary:
        Total:	7.4744 secs
        Slowest:	0.4002 secs
        Fastest:	0.0008 secs
        Average:	0.0727 secs
        Requests/sec:	1337.8936
        
        Total data:	440000 bytes
        Size/request:	44 bytes

        Response time histogram:
        0.001 [1]	|
        0.041 [2241]	|■■■■■■■■■■■■■■■■■■■■■
        0.081 [4259]	|■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        0.121 [2108]	|■■■■■■■■■■■■■■■■■■■■
        0.161 [729]	|■■■■■■■
        0.201 [344]	|■■■
        0.240 [156]	|■
        0.280 [103]	|■
        0.320 [35]	|
        0.360 [14]	|
        0.400 [10]	|


        Latency distribution:
        10% in 0.0116 secs
        25% in 0.0464 secs
        50% in 0.0600 secs
        75% in 0.0936 secs
        90% in 0.1403 secs
        95% in 0.1746 secs
        99% in 0.2533 secs

        Details (average, fastest, slowest):
        DNS+dialup:	0.0000 secs, 0.0008 secs, 0.4002 secs
        DNS-lookup:	0.0000 secs, 0.0000 secs, 0.0035 secs
        req write:	0.0000 secs, 0.0000 secs, 0.0016 secs
        resp wait:	0.0726 secs, 0.0008 secs, 0.4002 secs
        resp read:	0.0000 secs, 0.0000 secs, 0.0008 secs

        Status code distribution:
        [200]	10000 responses



        10000 Request prcessing time with only db read/write without asyncio


        Summary:
        Total:	15.1025 secs
        Slowest:	0.4291 secs
        Fastest:	0.0016 secs
        Average:	0.1493 secs
        Requests/sec:	662.1442
        
        Total data:	440000 bytes
        Size/request:	44 bytes

        Response time histogram:
        0.002 [1]	|
        0.044 [47]	|
        0.087 [283]	|■■
        0.130 [2675]	|■■■■■■■■■■■■■■■■■■■■■■
        0.173 [4954]	|■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        0.215 [1415]	|■■■■■■■■■■■
        0.258 [408]	|■■■
        0.301 [128]	|■
        0.344 [67]	|■
        0.386 [15]	|
        0.429 [7]	|


        Latency distribution:
        10% in 0.1050 secs
        25% in 0.1267 secs
        50% in 0.1436 secs
        75% in 0.1655 secs
        90% in 0.2007 secs
        95% in 0.2239 secs
        99% in 0.2963 secs

        Details (average, fastest, slowest):
        DNS+dialup:	0.0001 secs, 0.0016 secs, 0.4291 secs
        DNS-lookup:	0.0000 secs, 0.0000 secs, 0.0044 secs
        req write:	0.0000 secs, 0.0000 secs, 0.0013 secs
        resp wait:	0.1492 secs, 0.0015 secs, 0.4291 secs
        resp read:	0.0000 secs, 0.0000 secs, 0.0005 secs

        Status code distribution:
        [200]	10000 responses


With Caching

        10000 Request prcessing time read/write with asyncio

        Summary:
        Total:	0.8564 secs
        Slowest:	0.1409 secs
        Fastest:	0.0005 secs
        Average:	0.0080 secs
        Requests/sec:	11676.6190
        
        Total data:	310000 bytes
        Size/request:	31 bytes

        Response time histogram:
        0.000 [1]	|
        0.015 [9445]	|■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        0.029 [478]	|■■
        0.043 [9]	|
        0.057 [8]	|
        0.071 [6]	|
        0.085 [3]	|
        0.099 [6]	|
        0.113 [6]	|
        0.127 [1]	|
        0.141 [37]	|


        Latency distribution:
        10% in 0.0043 secs
        25% in 0.0056 secs
        50% in 0.0067 secs
        75% in 0.0079 secs
        90% in 0.0105 secs
        95% in 0.0150 secs
        99% in 0.0275 secs

        Details (average, fastest, slowest):
        DNS+dialup:	0.0001 secs, 0.0005 secs, 0.1409 secs
        DNS-lookup:	0.0000 secs, 0.0000 secs, 0.0044 secs
        req write:	0.0000 secs, 0.0000 secs, 0.0015 secs
        resp wait:	0.0079 secs, 0.0005 secs, 0.1329 secs
        resp read:	0.0000 secs, 0.0000 secs, 0.0030 secs

        Status code distribution:
        [405]	10000 responses

        10000 Request prcessing time with read/write without asyncio


        Summary:
        Total:	0.9661 secs
        Slowest:	0.2741 secs
        Fastest:	0.0003 secs
        Average:	0.0089 secs
        Requests/sec:	10350.5369
        
        Total data:	310000 bytes
        Size/request:	31 bytes

        Response time histogram:
        0.000 [1]	|
        0.028 [9846]	|■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        0.055 [102]	|
        0.082 [7]	|
        0.110 [8]	|
        0.137 [7]	|
        0.165 [8]	|
        0.192 [5]	|
        0.219 [6]	|
        0.247 [5]	|
        0.274 [5]	|


        Latency distribution:
        10% in 0.0040 secs
        25% in 0.0058 secs
        50% in 0.0073 secs
        75% in 0.0094 secs
        90% in 0.0122 secs
        95% in 0.0183 secs
        99% in 0.0312 secs

        Details (average, fastest, slowest):
        DNS+dialup:	0.0000 secs, 0.0003 secs, 0.2741 secs
        DNS-lookup:	0.0000 secs, 0.0000 secs, 0.0068 secs
        req write:	0.0000 secs, 0.0000 secs, 0.0041 secs
        resp wait:	0.0088 secs, 0.0003 secs, 0.2692 secs
        resp read:	0.0000 secs, 0.0000 secs, 0.0021 secs

        Status code distribution:
        [405]	10000 responses