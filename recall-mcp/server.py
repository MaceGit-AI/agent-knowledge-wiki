#!/usr/bin/env python3
"""knowledge-recall-mcp — lightweight hybrid recall over a markdown knowledge wiki.

Proven recipe (FTS5 + FastEmbed embeddings + sqlite-vec + Reciprocal-Rank-Fusion),
local-first, no API key. Point it at your wiki via the WIKI_DIR env var.

Usage:
  python server.py index            # (re)build the index over the wiki
  python server.py search "query"   # CLI hybrid search (shows results)
  python server.py read <path>      # print a note
  python server.py serve            # run as an MCP server (stdio)

Config via env: WIKI_DIR, RECALL_DB, RECALL_MODEL.
"""
import os, sys, re, json, glob, sqlite3, hashlib
from pathlib import Path

# Pin the FastEmbed model cache to a PERSISTENT dir inside the repo (not the volatile
# OS %TEMP%, which Windows Storage Sense / Disk Cleanup wipes — that triggered a silent
# ~87 MB model re-download on the next reindex). The 384-dim MiniLM weights are a core
# runtime asset of the recall engine, so they live with it. Gitignored via .fastembed_cache/.
os.environ.setdefault(
    "FASTEMBED_CACHE_PATH",
    str(Path(__file__).resolve().parent / ".fastembed_cache"),
)
# Load the model fully OFFLINE once it is cached locally. huggingface_hub otherwise
# revalidates the cached weights over the network on every load; under a client that
# spawns this server inside a restricted network namespace (corporate VPN/proxy, slow
# or blocked egress) that metadata check stalls for *minutes* with no timeout — the
# "reindex/search hangs forever" symptom — even though the 87 MB weights are right here.
# The weights ship in .fastembed_cache, so offline load is purely local and instant.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# Default points at the sibling Wiki/ in this repo; override with the WIKI_DIR env var.
WIKI_DIR = Path(os.environ.get("WIKI_DIR", str(Path(__file__).resolve().parent.parent / "Wiki")))
# Extra roots to index alongside the wiki — e.g. per-project ".memory" dirs (";"-separated).
# Strictly opt-in registered paths; never index unrelated repos.
EXTRA_DIRS = [Path(p) for p in os.environ.get("RECALL_EXTRA_DIRS", "").split(";") if p.strip()]
DB_PATH  = Path(os.environ.get("RECALL_DB", str(Path(__file__).parent / "recall-index.sqlite")))
MODEL    = os.environ.get("RECALL_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DIM      = 384
CHUNK, OVERLAP = 2000, 200
RRF_K    = 60
# Model-aware index key: embeddings from different models/chunkings are NOT comparable.
# The key is stored in the DB; do_index forces a full re-embed on mismatch, do_search
# refuses semantic search against a foreign-keyed index (content-hash alone would
# silently skip unchanged files after a model switch and mix vector spaces).
INDEX_KEY = f"{MODEL}|dim={DIM}|chunk={CHUNK}/{OVERLAP}|schema=1"
# Append-only retrieval log (review-queue input for retros — never automatic decisions).
LOG_PATH = Path(os.environ.get("RECALL_LOG", str(DB_PATH.parent / "recall-retrieval-log.jsonl")))

# Import the native-extension modules HERE, at module load on the MAIN thread.
# FastMCP runs sync tools on a worker thread, and a *first* import of a C-extension
# (sqlite_vec, fastembed/onnxruntime) from a worker thread can deadlock on Python's
# import lock — intermittently (a race). That was the real "recall hangs for minutes,
# but sometimes returns in ~1s" bug: the hang was `import sqlite_vec` inside the tool
# call, not the model or the network. Importing up front on the main thread makes the
# in-function imports cache hits, so no worker-thread first-import can ever deadlock.
import sqlite_vec as _sqlite_vec_preload          # noqa: F401  (preload on main thread)
try:
    import fastembed as _fastembed_preload        # noqa: F401  (preload on main thread)
except Exception:
    pass

_model = None
def _embed(texts):
    global _model
    from fastembed import TextEmbedding
    if _model is None:
        _model = TextEmbedding(model_name=MODEL)
    return [list(map(float, v)) for v in _model.embed(list(texts))]

def _blob(v):
    import sqlite_vec
    return sqlite_vec.serialize_float32(v)

def _db():
    import sqlite_vec
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    db.executescript(f"""
        CREATE TABLE IF NOT EXISTS notes(path TEXT PRIMARY KEY, title TEXT, hash TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(path UNINDEXED, title, content);
        CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY, path TEXT, text TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS vchunks USING vec0(embedding float[{DIM}] distance_metric=cosine);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
    """)
    return db

def _stored_key(db):
    row = db.execute("SELECT value FROM meta WHERE key='index_key'").fetchone()
    return row["value"] if row else None

_META_FIELDS = ("Summary", "Type", "Status", "Last updated")
def _page_meta(path):
    """Frontmatter-ish page metadata for richer search results (summary-first recall)."""
    try:
        head = Path(path).read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return {}
    meta = {}
    m = (re.search(r"^\*\*Summary\*\*:\s*(.+)$", head, re.M)
         or re.search(r"^description:\s*[\"']?(.+?)[\"']?\s*$", head, re.M))
    if m:
        meta["summary"] = m.group(1).strip()[:300]
    for field in ("Type", "Status"):
        m = re.search(rf"^\*\*{field}\*\*:\s*(.+)$", head, re.M)
        if m:
            meta[field.lower()] = m.group(1).strip()[:60]
    m = re.search(r"^\*\*Last updated\*\*:\s*(.+)$", head, re.M)
    if m:
        meta["last_updated"] = m.group(1).strip()[:20]
    return meta

def _log_retrieval(query, mode, results):
    """Append-only usage log — review-queue material, never an automatic signal."""
    try:
        import datetime
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                "q": query[:120], "mode": mode,
                "hits": [r["path"].rsplit("/", 1)[-1] for r in results],
            }, ensure_ascii=False) + "\n")
    except OSError:
        pass

def _chunk(text):
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i+CHUNK]); i += CHUNK - OVERLAP
    return out or [""]

def _drop(db, path):
    db.execute("DELETE FROM notes WHERE path=?", (path,))
    db.execute("DELETE FROM notes_fts WHERE path=?", (path,))
    for r in db.execute("SELECT id FROM chunks WHERE path=?", (path,)).fetchall():
        db.execute("DELETE FROM vchunks WHERE rowid=?", (r["id"],))
    db.execute("DELETE FROM chunks WHERE path=?", (path,))

def do_index():
    db = _db()
    # Model-aware index key: on mismatch (or a legacy DB without a key), force a FULL
    # re-embed — the content-hash shortcut below would otherwise keep foreign vectors.
    stored = _stored_key(db)
    has_notes = db.execute("SELECT 1 FROM notes LIMIT 1").fetchone() is not None
    force = has_notes and stored != INDEX_KEY
    files = []
    for _root in [WIKI_DIR] + EXTRA_DIRS:
        files += [Path(p) for p in glob.glob(str(_root / "**" / "*.md"), recursive=True)]
    seen, changed = set(), 0
    for f in files:
        rel = str(f).replace("\\", "/"); seen.add(rel)
        content = f.read_text(encoding="utf-8", errors="replace")
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()
        row = db.execute("SELECT hash FROM notes WHERE path=?", (rel,)).fetchone()
        if row and row["hash"] == h and not force:
            continue
        title = next((l[2:].strip() for l in content.splitlines() if l.startswith("# ")), f.stem)
        _drop(db, rel)
        db.execute("INSERT INTO notes(path,title,hash) VALUES(?,?,?)", (rel, title, h))
        db.execute("INSERT INTO notes_fts(path,title,content) VALUES(?,?,?)", (rel, title, content))
        chs = _chunk(content)
        for ch, v in zip(chs, _embed(chs)):
            cur = db.execute("INSERT INTO chunks(path,text) VALUES(?,?)", (rel, ch))
            db.execute("INSERT INTO vchunks(rowid,embedding) VALUES(?,?)", (cur.lastrowid, _blob(v)))
        changed += 1
    for r in db.execute("SELECT path FROM notes").fetchall():
        if r["path"] not in seen:
            _drop(db, r["path"])
    db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('index_key',?)", (INDEX_KEY,))
    db.commit()
    return {"wiki_dir": str(WIKI_DIR), "indexed_files": len(seen), "reembedded": changed,
            "index_key": INDEX_KEY, "forced_full_reembed": force}

def do_search(query, mode="hybrid", limit=8):
    db = _db()
    if mode in ("hybrid", "semantic"):
        stored = _stored_key(db)
        if stored is not None and stored != INDEX_KEY:
            raise ValueError(
                f"recall index was built with '{stored}' but this process runs "
                f"'{INDEX_KEY}' — semantic scores would be garbage. Re-run "
                f"`server.py index` with the current env (forces a full re-embed), "
                f"or fix RECALL_MODEL/RECALL_DB to match.")
    hits = {}
    if mode in ("hybrid", "fulltext"):
        q = " OR ".join(re.findall(r"\w+", query)) or query
        try:
            rows = db.execute(
                "SELECT path, snippet(notes_fts,2,'[',']','…',15) snip "
                "FROM notes_fts WHERE notes_fts MATCH ? ORDER BY bm25(notes_fts) LIMIT ?",
                (q, limit * 3)).fetchall()
            for rank, r in enumerate(rows):
                e = hits.setdefault(r["path"], {"score": 0.0, "snip": None, "modes": set()})
                e["score"] += 1.0 / (RRF_K + rank); e["snip"] = e["snip"] or r["snip"]; e["modes"].add("fts")
        except sqlite3.OperationalError:
            pass
    if mode in ("hybrid", "semantic"):
        qv = _blob(_embed([query])[0])
        rows = db.execute(
            "SELECT rowid, distance FROM vchunks WHERE embedding MATCH ? ORDER BY distance LIMIT ?",
            (qv, limit * 3)).fetchall()
        for rank, r in enumerate(rows):
            ch = db.execute("SELECT path, text FROM chunks WHERE id=?", (r["rowid"],)).fetchone()
            if not ch:
                continue
            e = hits.setdefault(ch["path"], {"score": 0.0, "snip": None, "modes": set()})
            e["score"] += 1.0 / (RRF_K + rank)
            if not e["snip"]:
                e["snip"] = " ".join(ch["text"][:160].split()) + "…"
            e["modes"].add("sem")
    out = []
    for path, e in sorted(hits.items(), key=lambda x: -x[1]["score"])[:limit]:
        t = db.execute("SELECT title FROM notes WHERE path=?", (path,)).fetchone()
        r = {"path": path, "title": t["title"] if t else path,
             "snippet": e["snip"], "score": round(e["score"], 4),
             "mode": "+".join(sorted(e["modes"]))}
        r.update(_page_meta(path))   # summary/type/status/last_updated when present
        out.append(r)
    _log_retrieval(query, mode, out)
    return out

def do_read(path):
    p = Path(path)
    if not p.is_absolute():
        p = WIKI_DIR / path
    return p.read_text(encoding="utf-8", errors="replace")

def serve():
    from fastmcp import FastMCP
    mcp = FastMCP("knowledge-recall")

    @mcp.tool()
    def search_notes(query: str, mode: str = "hybrid", limit: int = 8) -> list:
        """Hybrid (keyword + semantic) recall over the knowledge wiki. mode: hybrid|fulltext|semantic."""
        return do_search(query, mode, limit)

    @mcp.tool()
    def read_note(path: str) -> str:
        """Read a wiki note by path (relative to the wiki dir or absolute)."""
        return do_read(path)

    @mcp.tool()
    def reindex() -> dict:
        """Rebuild the recall index over the wiki (incremental by content hash)."""
        return do_index()

    mcp.run()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if cmd == "index":
        print(json.dumps(do_index(), indent=2))
    elif cmd == "search":
        print(json.dumps(do_search(" ".join(sys.argv[2:])), indent=2, ensure_ascii=False))
    elif cmd == "read":
        print(do_read(sys.argv[2]))
    else:
        serve()
