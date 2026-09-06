<!-- Topology + trace are generated: `python assets/build_svgs.py` -->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/system-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/system-light.svg">
  <img alt="shardul.sys — service topology: client → edge/gateway → services → postgres, redis, pgvector" src="assets/system-dark.svg" width="100%">
</picture>

```http
GET /whoami HTTP/1.1
Host: shardul.sys

HTTP/1.1 200 OK
content-type: application/json
```

```json
{
  "name":    "Shardul Shripad Hingane",
  "role":    "backend & AI systems engineer",
  "host":    "SGGS Nanded · B.Tech IT · 2024→2027 · CGPA 8.5",
  "runtime": "async python · fastapi · postgres · redis",
  "solved":  "400+ DSA problems, still counting",

  "thesis": [
    "a queue that loses jobs was never a queue",
    "a cache that lies is worse than no cache at all",
    "an LLM call with no fallback is a single point of failure"
  ],

  "status":  "shipping · open to backend / AI-infra work"
}
```

---

## `GET /services`

The stuff I've actually put into production, and what each one is worth.

| service | responsibility | stack | measured |
|---|---|---|---|
| **[`svc/codity`](https://github.com/Shardul9999/Distributed-Job-Scheduler)** | distributed job scheduler — Postgres *is* the broker | FastAPI · PG16 · Next.js · Docker | exactly-once across 10 workers × 500 jobs · 58 endpoints · 48 CI tests |
| **[`svc/readr`](https://github.com/Shardul9999/ai-pdf-chatbot-langchain)** | RAG over PDFs, isolated per user and per thread | Next.js · LangGraph · pgvector · Groq | ~200ms parse · ~1.3s embed · ~500ms retrieve |
| **[`svc/url-shortener`](https://github.com/Shardul9999/url-shortener)** | redirects + analytics, SSRF-hardened · [`live docs`](https://url-shortener-672q.onrender.com/docs) | FastAPI · Redis · Docker | 40ms → 6.7ms · 22 tests at 94% coverage |
| **[`svc/support-copilot`](https://github.com/Shardul9999/fastapi-ai-support-copilot)** | multi-tenant support backend | FastAPI · SQLAlchemy · Alembic · pgvector | tenant-scoped, migrations under version control |
| **[`svc/ai-gateway`](https://github.com/Shardul9999/AI-Fallback-Gateway)** | multi-provider LLM failover | Python · FastAPI | a dead provider ≠ a dead request |
| **[`lab/pg-tuning`](https://github.com/Shardul9999/postgresql_performance_tuining)** | 1M synthetic rows, read the plan before the code | PostgreSQL · B-Tree · GIN | up to 20,000× on the worst offenders |
| **[`svc/cloudbeat`](https://github.com/Shardul9999/CloudBeat)** | 3D music player over Spotify OAuth | React · Flask · Spline · Supabase | 60fps GPU scene |

---

## `GET /traces`

Two paths I measured rather than guessed at.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/trace-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/trace-light.svg">
  <img alt="Trace waterfall: GET /{slug} cold 40ms vs cached 6.7ms; readr ingest pipeline parse 200ms, embed 1.3s, retrieve 500ms, then SSE stream" src="assets/trace-dark.svg" width="100%">
</picture>

---

## `GET /decisions`

Anyone can list tools. These are the calls I made and what they cost me.

<details>
<summary><b>ADR-001</b> — Postgres is the queue. No Redis broker, no RabbitMQ.</summary>

<br>

**Context.** Codity needed background jobs to run exactly once across a worker fleet, including when a worker dies mid-job.

**Decision.** Make Postgres the broker. Workers claim disjoint batches with `SELECT … FOR UPDATE SKIP LOCKED`, hold a fencing token so a zombie process can't complete work it no longer owns, and heartbeat while running. A leader-elected reaper nulls the stale lock tokens of dead workers and revives their jobs.

**Consequence.** One less system to operate, and job state commits in the *same transaction* as the business data it belongs to — no dual-write problem. The ceiling is now Postgres throughput. At this scale that's a trade worth making; at 100× it stops being one, and I'd want to know that before I got there.

</details>

<details>
<summary><b>ADR-002</b> — Cache-aside for redirects, never write-through.</summary>

<br>

**Context.** `GET /{slug}` is a read-dominated hot path where a cold lookup cost 40ms.

**Decision.** Cache-aside in Redis, TTL-bounded. Rate limiting is a sliding window built from atomic Redis pipelines, so the check itself can't race.

**Consequence.** 6.7ms warm — roughly 6× faster. Staleness is bounded by the TTL, and the important part is structural: the cache is an optimization, so a cold Redis degrades latency instead of correctness.

</details>

<details>
<summary><b>ADR-003</b> — Fail over to another provider instead of retrying harder.</summary>

<br>

**Context.** A single LLM vendor is a single point of failure, and retrying against a provider that is *down* just spends the user's latency budget for nothing.

**Decision.** Route through a gateway with an ordered provider chain, and treat a failover hop as part of the latency budget rather than an exception.

**Consequence.** Provider incidents degrade instead of page. The cost is that the budget has to absorb one dead hop, so timeouts must be tight enough that the second provider still has room to answer.

</details>

<details>
<summary><b>ADR-004</b> — Read the query plan before rewriting the query.</summary>

<br>

**Context.** 1M synthetic rows and a set of queries that were, charitably, slow.

**Decision.** `EXPLAIN ANALYZE` first, every time. Then targeted B-Tree and GIN indexes against what the planner actually did — not what I assumed it did.

**Consequence.** Up to 20,000× on the worst offenders, without touching application code. Indexes aren't free: they cost write throughput and disk, which is exactly why they should follow evidence instead of instinct.

</details>

---

## `GET /runtime`

```toml
# shardul.sys/runtime.toml

[languages]
fluent  = ["python", "sql"]
working = ["java", "typescript"]

[backend]
core     = ["fastapi", "sqlalchemy", "alembic", "asyncio"]
storage  = ["postgresql", "redis", "pgvector", "supabase"]
patterns = ["cache-aside", "sliding-window rate limits", "SKIP LOCKED queues",
            "leader election", "fencing tokens", "dead-letter queues"]

[ai]
orchestration = ["langgraph", "langchain"]
inference     = ["groq", "gemini"]
retrieval     = ["pgvector cosine top-k", "chunking + embeddings"]

[ops]
ship = ["docker", "github actions", "render", "vercel", "gcp", "linux"]
test = ["pytest", "real postgres in CI — not sqlite"]
```

---

## `GET /queue`

```
●  shipping     readr — production RAG on langgraph · supabase pgvector · groq
◐  sharpening   backend fundamentals — async python, caching, database internals
○  exploring    multi-agent systems and orchestration patterns
```

---

## `GET /traffic`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Shardul9999/Shardul9999/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Shardul9999/Shardul9999/output/github-contribution-grid-snake.svg">
  <img alt="Contribution graph consumed by a snake" src="https://raw.githubusercontent.com/Shardul9999/Shardul9999/output/github-contribution-grid-snake.svg" width="100%">
</picture>

---

## `GET /health`

```json
{
  "status": "up",
  "region": "in-nanded-1",
  "links": {
    "portfolio": "shardul-portfolio-iota.vercel.app",
    "linkedin":  "in/ShardulHingane",
    "leetcode":  "u/shardul_16",
    "email":     "shardulhingane16@gmail.com"
  }
}
```

**[portfolio](https://shardul-portfolio-iota.vercel.app/)** · **[linkedin](https://linkedin.com/in/ShardulHingane)** · **[leetcode](https://leetcode.com/u/shardul_16/)** · **[email](mailto:shardulhingane16@gmail.com)**

<sub>Everything above is generated from a script in <a href="assets/build_svgs.py"><code>assets/</code></a> — no third-party stat services, no tracking pixels, nothing that can 404 on me.</sub>
