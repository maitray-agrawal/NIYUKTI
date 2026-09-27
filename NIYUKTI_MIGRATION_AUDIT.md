# NIYUKTI — Comprehensive Migration, Rebrand & Deployment Audit

**Document:** `NIYUKTI_MIGRATION_AUDIT.md`  
**Date:** September 2026  
**System:** ASTRA / NIYUKTI — AI-Powered Talent Intelligence  
**Repository:** `d:\TalentMindAI`  
**Target Brand:** **ASTRA / NIYUKTI** (Sanskrit: नियुक्ति — appointment, employment, placement)  
**Descriptor:** *AI-Powered Talent Intelligence*  
**Canonical Copy:**  
> NIYUKTI is an AI-powered talent intelligence and recruitment platform that intelligently matches candidates with job requirements, ranks applicants based on skills and experience, identifies skill gaps, and provides explainable hiring insights to help recruiters make faster, more informed decisions.

---

## 1. Executive Summary & Audit Objectives

This audit establishes the pre-migration baseline of the entire repository before executing the brand transformation and production hardening. The objective is to transition the application from **TalentMindAI** to **NIYUKTI** under the **ASTRA** product umbrella while:
1. Preserving all existing capabilities (100,001 candidate capacity, candidate search, hybrid ranking, XAI explanations, Groq LLM reranking, candidate comparison, skill-gap analysis, recruiter copilot, and Hack2Skill submission generation).
2. Fixing the production frontend deployment on Vercel (resolving the raw unstyled HTML issue).
3. Ensuring seamless PostgreSQL (Render) and Vercel API proxy compatibility without hardcoded development-machine paths or localhost assumptions.
4. Adhering to zero fabricated metrics or unsupported enterprise guarantees.

---

## 2. Global Pattern Search & Categorization

A full-codebase scan (excluding `.git`, `venv`, large `.db` binaries, and challenge raw archives) was executed. Results are cataloged below:

### 2.1 Brand Patterns

| Search Term | Matches | Occurrences by Area | Classification & Planned Action |
|:---|:---:|:---|:---|
| `TalentMindAI` | 22 | `README.md` (2), `docs/*.md` (10), `backend/services/*.py` (2), `backend/*.py` (4), `vercel.json` (1), `DEPLOYMENT_AUDIT.md` (3) | **USER-FACING / DOCS:** Rebrand to `NIYUKTI` or `ASTRA / NIYUKTI`. Retain in historical audit notes as needed. |
| `TalentMind` | 92 | `frontend_screens/*.html` (25), `frontend_screens/integration.js` (1), `backend/app/main.py` (1), `backend/app/config.py` (2), `backend/app/services/copilot_service.py` (2), `docs/*.md` (20), `backend/tests/*.py` (12), `render.yaml` (1) | **USER-FACING:** Rebrand all HTML `<title>`, headings, footers, copilot prompt strings, and user-facing copies to `NIYUKTI`. **INTERNAL:** Retain test file names / DB file references where internal or migration-safe. |
| `talentmind` | 92 | Identical case-insensitive matches across doc files, database file references (`talentmind.db`), and email domains (`@talentmind.io`). | Keep database table schemas unchanged; update placeholder email domains and user-facing strings. |
| `TALENTMIND` | 0 | None found. | No action required. |
| `Talent Mind` | 0 | None found. | No action required. |
| `talent-mind` | 0 | None found. | No action required. |

### 2.2 Network & Environment Patterns

| Search Pattern | Count | Locations | Status & Action |
|:---|:---:|:---|:---|
| `127.0.0.1` | 20 | `main.py` (CORS), `integration.js` (comment), `.env.example`, `demo_runbook.md`, `README.md`, `DEPLOYMENT_AUDIT.md` | **SAFE:** `integration.js` already uses dynamic fallback `(window.__ENV__ && window.__ENV__.API_BASE) \|\| '/api'`. Add live Vercel domain to `main.py` CORS list. |
| `localhost` | 8 | `config.py` (default `FRONTEND_URL`), `main.py` (CORS), `.env.example`, `DEPLOYMENT_AUDIT.md` | **SAFE:** Kept for local development while `FRONTEND_URL` is parameterized for production. |
| `d:\TalentMindAI` / `D:\TalentMindAI` | 1 | Historical reference in `DEPLOYMENT_AUDIT.md`. | **SAFE:** All production backend routes (`candidates.py`, `ranking.py`, `submission.py`) now use relative/dynamic `Path` structures. Verified no production path leaks. |
| `C:\Users` | 0 | None in production code (only temporary image links in non-runtime docs). | **SAFE:** No user-facing leaks. |
| `file://` | 7 | `README.md`, `test_copilot_integration.py`, `scratch/*.py`, `docs/*.md` | **SAFE:** Used in Playwright local test scripts. |
| `http://` | 23 | Local dev URLs, schema namespace URLs (`http://schema.org`). | **SAFE:** Production endpoints use `https://` or relative `/api/*`. |
| `https://` | 66 | CDNs (Tailwind, Google Fonts), live Render URL in `vercel.json`. | **VERIFIED:** Third-party CDNs and Render destination are valid. |
| `API_BASE` | 37 | `frontend_screens/integration.js` | **ACTIVE:** Dynamically resolves to `'/api'`, routing through Vercel proxy. |
| `DATABASE_URL` | 21 | `config.py`, `database.py`, `render.yaml`, `.env.example`, tests | **ACTIVE:** Defaults to SQLite locally; takes PostgreSQL connection string in production. |
| `GROQ_API_KEY` | 23 | `config.py`, `main.py`, services, docs | **ACTIVE:** Read from environment variable; never hardcoded; graceful fallback implemented. |
| `FRONTEND_URL` | 8 | `config.py`, `main.py`, `render.yaml`, `.env.example` | **ACTIVE:** Used to configure production CORS origin. |

---

## 3. Frontend Architecture & Vercel Root Cause Analysis

### 3.1 The Broken Production Landing Page (Root Cause Identified)
- **Symptom:** Vercel live URL (`https://talentmindai-app.vercel.app`) loads as raw, unstyled HTML with a plain bullet list.
- **Root Cause:** A 32-line unstyled `frontend_screens/index.html` was manually created containing raw `<h1>TalentMind AI</h1>` and an unstyled `<ul>` with no CSS links, no Tailwind CDN, and no `integration.js` script. Because Vercel serves `frontend_screens/` statically, requests to `/` resolve directly to `index.html`.
- **Existing Styled Architecture:** All feature screens (`dashboard.html`, `candidate_search.html`, `candidate_ranking.html`, `candidate_details.html`, `candidate_comparison.html`, `skill_gap_analysis.html`, `recruiter_copilot.html`, `settings.html`) use **Tailwind CSS via CDN**, **Google Fonts (Geist & Inter)**, and **Material Symbols**, combined with custom dark-mode tokens and glassmorphism CSS in inline `<style>` tags.
- **Resolution Plan:**
  1. Replace `frontend_screens/index.html` with a styled NIYUKTI portal / executive command dashboard that matches the dark obsidian aesthetic, imports Tailwind and Google Fonts, provides instant navigation cards to all 6 modules, and includes an auto-redirect / quick-launch to `/dashboard.html`.
  2. Add `<link rel="icon" type="image/svg+xml" href="/favicon.svg">` with a geometric 'N' / NIYUKTI mark.
  3. Inject proper SEO and OpenGraph metadata (`<meta name="description">`, `<meta property="og:title">`, `<meta property="og:description">`) into every HTML screen.

### 3.2 Frontend Rebranding Scope (HTML & JS)

| File | Current Title / Header | Target NIYUKTI Branding |
|:---|:---|:---|
| `dashboard.html` | `TalentMind AI \| Obsidian Intelligence Dashboard` | `NIYUKTI — AI-Powered Talent Intelligence \| Dashboard` |
| `candidate_search.html` | `TalentMind AI \| Candidate Search` | `NIYUKTI — Candidate Search \| AI Talent Intelligence` |
| `candidate_ranking.html` | `TalentMind AI \| Candidate Ranking` | `NIYUKTI — Explainable Candidate Ranking` |
| `candidate_details.html` | `Candidate Details \| TalentMind AI` | `NIYUKTI — Candidate Profile & XAI Insights` |
| `candidate_comparison.html` | `Candidate Comparison \| TalentMind AI` | `NIYUKTI — Candidate Comparison` |
| `skill_gap_analysis.html` | `TalentMind AI \| Skill Gap Analysis` | `NIYUKTI — Skill Gap Analysis` |
| `recruiter_copilot.html` | `TalentMind AI \| Recruiter Copilot` | `NIYUKTI Copilot — AI Recruitment Assistant` |
| `settings.html` | `Settings \| TalentMind AI` | `NIYUKTI — Settings & System Configuration` |
| `index.html` | `TalentMind AI` (unstyled) | `NIYUKTI — AI-Powered Talent Intelligence` (Executive Portal) |
| `integration.js` | `* TalentMind AI - Frontend/Backend Integration System` | `* NIYUKTI - Frontend/Backend Integration System` |

Sidebar header across all screens will be unified to:
```html
<div class="flex items-center gap-3 px-2 mb-10">
  <div class="w-10 h-10 rounded-lg bg-primary-container flex items-center justify-center">
    <span class="material-symbols-outlined text-on-primary-container" style="font-variation-settings: 'FILL' 1;">psychology</span>
  </div>
  <div>
    <span class="text-[10px] font-bold tracking-widest text-primary/80 uppercase block">ASTRA</span>
    <h1 class="font-headline-md text-headline-md font-bold text-primary dark:text-primary-fixed leading-none">NIYUKTI</h1>
    <p class="font-label-sm text-[11px] text-on-surface-variant/70 tracking-tight mt-0.5">AI Talent Intelligence</p>
  </div>
</div>
```

---

## 4. Backend Architecture, Database & PostgreSQL Compatibility

### 4.1 FastAPI Service Configuration
- **Entrypoint:** `backend/app/main.py` (`app.main:app`).
- **Title & Description:**
  - *Current:* `"TalentMind AI Recruitment Platform Backend"`
  - *Target:* `"NIYUKTI — AI-Powered Talent Intelligence API"` / `"ASTRA / NIYUKTI: AI-Powered Talent Intelligence and Recruitment Platform Backend."`
- **CORS:** Currently allows `[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5500", "http://127.0.0.1:3000", "http://127.0.0.1:5500"]`.
  - *Action:* Add `"https://talentmindai-app.vercel.app"` explicitly as an allowed origin to ensure the live production frontend is always accepted regardless of environment variable propagation.

### 4.2 Database & PostgreSQL Compatibility Audit
- **Engine Creation (`database.py`):** Verified conditional `check_same_thread: False` only applies when `DATABASE_URL` starts with `sqlite`. PostgreSQL connections receive standard connection arguments without invalid SQLite parameters.
- **SQLAlchemy Models (`models/`):** All models inherit from `Base` with standard types (`Integer`, `String`, `Float`, `JSON`, `Text`).
- **PostgreSQL JSON Compatibility Finding:**
  - In `backend/app/routes/candidates.py` (lines 49-50, 129, 138), the code previously called `func.json_extract(...)`.
  - In PostgreSQL, `json_extract()` is not a native function (SQLite-specific).
  - *Remediation:*
    1. For `location` search: Replace `func.json_extract(Candidate.profile, '$.location')` with direct column filtering `Candidate.location.ilike(f"%{location}%")` because `location` is already an indexed column on `Candidate`.
    2. For `open_to_work` and `profile_completeness` in stats: Make JSON signal extraction dialect-aware: check `db.bind.dialect.name == "sqlite"` to use `func.json_extract` for SQLite, or standard JSON operators for PostgreSQL.

---

## 5. AI Services & Feature Preservation

### 5.1 Hybrid Ranking Engine (`ranker_service.py`)
- **Formula:** Multi-attribute weighted score:
  - Skills Match: 30%
  - Experience Match: 20%
  - Semantic/Keyword Relevance: 15%
  - Education Level: 15%
  - Deterministic Behavioral Signals (completeness, response rate, tenure): 10%
  - Location/Work Preference: 10%
- **Status:** 100% deterministic heuristic baseline. Explainable breakdown is returned with matched skills, missing skills, and detailed penalty points.
- **Verification:** Preserved without modification to algorithm weights or contracts.

### 5.2 Groq LLM Reranker (`groq_reranker.py`)
- **Model:** `llama-3.3-70b-versatile` via Groq REST API.
- **Timeout & Retries:** 30s timeout with exponential backoff.
- **Fallback:** If `GROQ_API_KEY` is not configured or an API error occurs, system logs warning and gracefully preserves heuristic rankings with `is_groq_evaluated: False`. No crashes occur.
- **Branding:** Update `User-Agent: TalentMindAI/1.0` -> `User-Agent: NIYUKTI/1.0`.

### 5.3 Recruiter Copilot (`copilot_service.py`)
- **System Prompt:** Update internal prompt from `"(TalentMind Recruiter Copilot)"` to `"(NIYUKTI Recruiter Copilot)"`.
- **Outreach Email Template:** Update `"our TalentMind platform"` to `"our NIYUKTI platform"`.
- **Safety:** Contextual injection handles missing candidate/job details safely without hallucination.

### 5.4 Hack2Skill Submission Generator (`submission.py`)
- **Schema Compliance:** Generates CSV with exact headers `candidate_id,rank,score,reasoning`.
- **Ordering:** Strictly validates descending score order, unique contiguous ranks (1..100), and non-empty structured reasoning.
- **Path Portability:** Saves to workspace root using `BASE_DIR.parent / "submission.csv"` without hardcoded OS paths.

---

## 6. Test Suite Baseline

| Test File | Total | Passed | Failed | Root Cause of Failure |
|:---|:---:|:---:|:---:|:---|
| `test_ranking_engine.py` | 6 | 6 | 0 | Fully passing |
| `test_submission.py` | 1 | 1 | 0 | Fully passing |
| `test_ingestion.py` | 3 | 3 | 0 | Fully passing |
| `test_jd_intelligence.py` | 11 | 11 | 0 | Fully passing |
| `test_backend.py` | 6 | 5 | 1 | `test_2_candidate_crud_routes` calls `read_candidates(db=self.db)` directly without FastAPI request context; `limit` and `offset` default to `Query` objects, causing `int(Query)` TypeError. |
| `test_copilot_integration.py` | 4 | 1 | 3 | Playwright browser tests expecting live server on port 8000 when running offline. |

*Action:* Fix parameter unwrapping in `candidates.py` (`val = getattr(param, 'default', 0) if not isinstance(param, int) else param`) so `test_backend.py` achieves 6/6 (100% pass).

---

## 7. Migration Checklist

- [x] Complete repository audit and issue mapping.
- [x] Author `NIYUKTI_MIGRATION_AUDIT.md`.
- [ ] Create `frontend_screens/favicon.svg` with modern NIYUKTI branding mark.
- [ ] Rebrand `index.html` to styled NIYUKTI Executive Portal with navigation cards and redirect.
- [ ] Rebrand all 8 feature HTML screens (titles, meta tags, sidebar, headers, footer).
- [ ] Update `integration.js` header comment and brand references.
- [ ] Update `vercel.json` rewrites (proxy `/api/*` and `/health`).
- [ ] Update backend `main.py` (project name, Swagger description, CORS origins, `/api/health` alias).
- [ ] Update `config.py` (PROJECT_NAME).
- [ ] Update `copilot_service.py`, `groq_reranker.py`, `groq_jd_service.py` branding and user agents.
- [ ] Fix `candidates.py` offset/limit Query coercion and PostgreSQL JSON compatibility.
- [ ] Update `render.yaml` service name (`niyukti-api`).
- [ ] Update `.env.example` with NIYUKTI documentation.
- [ ] Create `API_AUDIT.md`.
- [ ] Create `DEPLOYMENT_VERIFICATION.md`.
- [ ] Rewrite `README.md` with complete NIYUKTI documentation and architecture diagrams.
- [ ] Re-run test suite and verify 100% pass rate.
