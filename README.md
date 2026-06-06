# FDA 510(k) Submission Assistant

AI drafting assistant that helps medical device companies prepare **510(k) submissions**. Upload any materials — notes, specs, PDFs, slide decks — and receive:

- **Submission Package** — complete eSTAR-structured draft (HTML + JSON) even from minimal input
- Gap analysis mapped to eSTAR sections
- Ranked predicate device recommendations (K-numbers + rationale)
- Substantial equivalence comparison draft
- Full eSTAR section drafts (LLM or template fallback)
- Anticipated FDA reviewer questions

**This is a drafting assistant only.** All outputs require human regulatory review before submission. Do not auto-submit to FDA.

## Quick start

### 1. Install dependencies

```bash
cd Project_June
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. Import the 510(k) database (one-time, ~5–10 min)

```bash
python scripts/import_510k_db.py
```

This streams `device-510k-0001-of-0001.json` into `storage/sqlite/510k.db`.

### 3. Start Ollama (optional but recommended)

```bash
ollama serve
ollama pull qwen2.5:3b
```

If Ollama is unavailable, the agent falls back to heuristic extraction.

### 4. Launch the web UI

```bash
streamlit run app/streamlit_app.py
```

Open http://localhost:8501 — upload anything, we'll figure out what you have.

## Project structure

```
src/fda_510k/     Core package (ingestion, extraction, tools, agent)
app/              Streamlit web UI
data/             eSTAR checklist, sample inputs
scripts/          Database import utilities
tests/            Unit tests
storage/          Uploads, SQLite DB, outputs (gitignored)
```

## Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Key settings: `OLLAMA_MODEL`, `FDA_510K_DB_PATH`, `ENABLE_OCR`.

## Running tests

```bash
# Import DB first for search/agent tests
python scripts/import_510k_db.py
pytest
```

## Disclaimers

- Drafting assistant only — not legal or regulatory advice
- openFDA data is not legally validated; verify against official FDA records
- Predicate chains are not in openFDA metadata (Phase 2: 510(k) Summary PDF parsing)
- All LLM content is marked **DRAFT — REQUIRES REGULATORY REVIEW**

## Phase roadmap

- **Phase 1 (current):** Universal intake, profile extraction, gap analysis, predicate search, SE draft, FDA questions, web UI
- **Phase 2:** FDA guidance RAG, 510(k) Summary PDF predicate extraction, recall cross-check
- **Phase 3:** eSTAR export helper, multi-turn refinement, audit log
