# NIYUKTI — API Audit & Endpoint Verification Matrix

**Document:** `API_AUDIT.md`  
**System:** ASTRA / NIYUKTI  
**Base Path:** `/api`  
**API Documentation:** Interactive Swagger UI at `/docs`, ReDoc at `/redoc`

---

## 1. Complete API Route Inventory

| Endpoint | Method | Purpose | Frontend Caller | Production Status |
|:---|:---:|:---|:---|:---:|
| `/` | `GET` | Root API metadata, project name, docs URL, prefix | Browser, uptime probes | **OPERATIONAL** (200 OK) |
| `/health` | `GET` | System health check (verifies DB ping & Groq key) | `integration.js` (`checkApiConnection`), Render health check | **OPERATIONAL** (200 OK / 503) |
| `/api/candidates/` | `GET` | Paginated candidate retrieval with filters (q, skills, exp, work mode) | `candidate_search.html`, `candidate_ranking.html` via `integration.js` | **OPERATIONAL** (200 OK, returns `X-Total-Count`) |
| `/api/candidates/` | `POST` | Create a new candidate record | Admin / API client | **OPERATIONAL** (201 Created) |
| `/api/candidates/search` | `GET` | Advanced search with multi-field filtering | API client / Search extensions | **OPERATIONAL** (200 OK) |
| `/api/candidates/stats` | `GET` | Aggregate talent pool metrics (total, experience distribution, top skills) | `dashboard.html` (`initDashboard()`) | **OPERATIONAL** (200 OK) |
| `/api/candidates/{id}` | `GET` | Retrieve full candidate profile, career history, skills, signals | `candidate_details.html`, `recruiter_copilot.html` | **OPERATIONAL** (200 OK / 404) |
| `/api/candidates/{id}` | `PUT` | Update candidate profile details or status | Sourcing workflow / API client | **OPERATIONAL** (200 OK) |
| `/api/candidates/{id}` | `DELETE` | Remove candidate record | Admin / API client | **OPERATIONAL** (200 OK) |
| `/api/candidates/compare` | `POST` | Multi-candidate comparative radar & skill gap analysis | `candidate_comparison.html` (`initCandidateComparison()`) | **OPERATIONAL** (200 OK) |
| `/api/candidates/import` | `POST` | Batch ingest JSONL candidates stream into database | CLI ingestion scripts / Admin | **OPERATIONAL** (200 OK) |
| `/api/candidates/{id}/explanation` | `GET` | Explainable AI (XAI) feature score breakdown and penalty reasons | `candidate_details.html` (`initCandidateDetails()`) | **OPERATIONAL** (200 OK) |
| `/api/jobs/` | `GET` | List active job requisitions | `dashboard.html`, `candidate_ranking.html`, `recruiter_copilot.html` | **OPERATIONAL** (200 OK) |
| `/api/jobs/` | `POST` | Create new job requisition | Job intake modal / API client | **OPERATIONAL** (201 Created) |
| `/api/jobs/analyze` | `POST` | Extract structured role requirements from raw JD text / docx | `dashboard.html` (`setupJdIntelligence()`) | **OPERATIONAL** (200 OK) |
| `/api/jobs/{id}` | `GET` | Retrieve job details, required skills, and preferences | `candidate_ranking.html`, `skill_gap_analysis.html` | **OPERATIONAL** (200 OK) |
| `/api/jobs/{id}` | `PUT` | Update job requisition details | Hiring manager / API client | **OPERATIONAL** (200 OK) |
| `/api/jobs/{id}` | `DELETE` | Remove job requisition | Admin / API client | **OPERATIONAL** (200 OK) |
| `/api/ranking/rank/{job_id}` | `POST` | Calculate deterministic 6-factor heuristic rankings for job | `candidate_ranking.html` (Rank action) | **OPERATIONAL** (200 OK) |
| `/api/ranking/job/{job_id}` | `GET` | Fetch ranked candidate list sorted by match score | `candidate_ranking.html`, `dashboard.html` | **OPERATIONAL** (200 OK) |
| `/api/ranking/rerank/{job_id}` | `POST` | Execute Groq LLM reranking on top candidate cohort | `candidate_ranking.html` (Rerank action) | **OPERATIONAL** (200 OK with heuristic fallback) |
| `/api/ranking/generate` | `POST` | On-the-fly candidate ranking against custom ad-hoc criteria | Dynamic ranking client | **OPERATIONAL** (200 OK) |
| `/api/ranking/candidate/{cid}/skill-gap/{jid}` | `GET` | Detailed skill gap breakdown (current, required, missing, match %) | `skill_gap_analysis.html` (`initSkillGapAnalysis()`) | **OPERATIONAL** (200 OK) |
| `/api/copilot/chat` | `POST` | Conversational recruiter copilot with candidate & job context | `recruiter_copilot.html` (`initRecruiterCopilot()`) | **OPERATIONAL** (200 OK with fallback generator) |
| `/api/submission/generate` | `POST` | Compile and validate official Hack2Skill `submission.csv` | Submission pipeline / evaluation scripts | **OPERATIONAL** (200 Streaming CSV) |

---

## 2. Frontend to Backend Request Architecture

```
User Browser
    │
    ▼
Vercel Edge (Frontend)
    │
    ├─► Static Assets (/dashboard.html, /candidate_search.html, /favicon.svg)
    │
    └─► /api/* (Rewritten by vercel.json)
    │     │
    │     ▼
    └─► Render Backend (FastAPI on https://talentmindai-rgar.onrender.com)
          │
          ├─► CORS Security Validation (allowed origins)
          ├─► SQLAlchemy Engine (SQLite local / PostgreSQL Render)
          └─► Groq Cloud API (Llama 3.3 70B Versatile, with offline heuristic fallback)
```

---

## 3. Resiliency & Error Handling Audit

1. **Database Fallback:**
   - SQLite locally (`check_same_thread: False`).
   - PostgreSQL in production via `DATABASE_URL` (standard pool, no invalid SQLite flags).
2. **Groq API Fallback:**
   - If `GROQ_API_KEY` is missing or fails (rate-limit 429, timeout), reranker logs a warning and returns heuristic rankings with `is_groq_evaluated: False`.
   - Copilot provides structured candidate summaries and outreach templates even if external LLM times out.
3. **Frontend Connection Indicator:**
   - `integration.js` polls `/health` (or `/api/health`) every 30s.
   - Live badge in header updates to `Live API Connected` or `Offline Mode` without interrupting page usage.
