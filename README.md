# NIYUKTI

### AI-Powered Talent Intelligence

Sanskrit: **नियुक्ति (Niyukti)** — *appointment, employment, placement, or engagement.*

**NIYUKTI** is an AI-powered talent intelligence and recruitment platform that intelligently matches candidates with job requirements, ranks applicants based on skills and experience, identifies skill gaps, and provides explainable hiring insights to help recruiters make faster, more informed decisions.

Part of the **ASTRA** ecosystem of intelligence tools, NIYUKTI combines deterministic multi-attribute candidate scoring, transparent Explainable AI (XAI) justifications, cognitive Groq LLM reranking, candidate comparison, and conversational recruiter assistance over a benchmarked pool of **100,001 candidates**.

---

## 1. Problem

Modern corporate recruitment suffers from critical operational bottlenecks:
- **Keyword-Stuffed Resumes & False Positives:** Traditional Applicant Tracking Systems (ATS) rely on naive boolean string matching, heavily penalizing qualified candidates who describe proficiencies uniquely while advancing low-fit applicants who over-index on keywords.
- **Black-Box AI Decisions:** Emerging generative tools score candidates without transparent justifications, leaving hiring managers unable to audit why a candidate was ranked high or disqualified.
- **Recruiter Burnout & Latency:** Manually parsing unstructured job descriptions, evaluating cross-functional skill overlaps, identifying specific skill gaps, and drafting personalized outreach requires hours per role.
- **Scale Bottlenecks:** Evaluating pools of 100,000+ candidates in real time causes database lockups, high memory usage, and costly LLM token spend if architectures lack layered filtering.

---

## 2. Solution

NIYUKTI provides a layered, transparent talent intelligence platform:
1. **Multi-Stage Funnel Architecture:** Low-latency deterministic pre-filtering across 100,001 profiles, followed by deep 6-factor heuristic scoring, with optional LLM reranking applied only to the top cohort.
2. **Transparent Explainable AI (XAI):** Clear visibility into score compositions (exact matched skills, identified gaps, seniority delta, and penalty factors).
3. **Cognitive Recruiter Decision Support:** In-context Recruiter Copilot powered by Groq (Llama 3.3 70B / 3.1 8B) for customized outreach emails, interview question planning, and candidate upskilling roadmaps.
4. **Hack2Skill Challenge-Validated:** Fully verified against the official India Runs Data and AI Challenge dataset and submission compliance validator.

---

## 3. Core Capabilities

- **100,001 Candidate Scale:** Single-query statistical aggregations and chunked database streaming (`yield_per`) prevent memory spikes.
- **Structured Job Description Parsing:** Upload or paste raw text or `.docx` job descriptions to automatically extract required skills, minimum experience, and location preferences via heuristic extraction or Groq LLM intelligence.
- **Candidate Discovery & Search:** Multi-attribute filtering across skills, experience thresholds, remote/hybrid preferences, and availability flags.
- **Explainable Hybrid Ranking:** 6-pillar multi-attribute scoring combining technical competency, experience alignment, TF-IDF semantic overlap, education prestige, behavioral signals, and work mode compatibility.
- **Groq LLM-Assisted Reranking:** Secondary cognitive pass evaluating top-ranked applicants with graceful offline fallback.
- **Candidate Comparison Matrix:** Side-by-side comparative radar and attribute benchmarking for final hiring rounds.
- **Deterministic Skill-Gap Analysis:** Delineates current verified skills vs. job requirements and highlights high-impact development areas.
- **NIYUKTI Recruiter Copilot:** Candidate-in-the-loop AI conversational assistant for outreach, profile summaries, and technical interview guides.
- **Challenge-Compliant Submission Compiler:** Automated export of official `submission.csv` adhering strictly to schema and ranking rules.

---

## 4. Architecture

NIYUKTI is deployed as a decoupled, production-hardened web application:

```
[ User Browser ]
       │
       ▼
[ Vercel Edge Network ]
  ├── Serves static UI (/dashboard.html, /candidate_search.html, /favicon.svg)
  └── Proxies /api/* & /health
       │
       ▼
[ Render Backend (FastAPI / ASGI) ]
  ├── CORS Origin Validation
  ├── REST Endpoints (/api/candidates, /api/jobs, /api/ranking, /api/copilot)
  ├── SQLAlchemy ORM (SQLite local / PostgreSQL on Render)
  └── Multi-Tiered AI Services
       ├── RankerService (Deterministic Heuristic Engine)
       ├── GroqReranker (Llama 3.3 70B via Groq Cloud)
       └── CopilotService (Llama 3.1 8B with Fallback Templates)
```

---

## 5. AI Components

NIYUKTI distinguishes clearly between **deterministic computation** and **generative LLM cognition**:

| Component | Technology | Nature | Role |
|:---|:---|:---:|:---|
| **JD Analyzer** | Regex Heuristic + Groq Llama 3.3 | Hybrid | Extracts structured requirements from unstructured text and `.docx` |
| **Semantic Overlap** | Scikit-learn TF-IDF Vectorizer | Deterministic | Evaluates cosine text similarity across resume and job contexts |
| **Heuristic Ranker** | Weighted Multi-Attribute Algorithm | Deterministic | Calculates calibrated 0–100 match scores across 6 objective dimensions |
| **Groq Reranker** | Groq REST API (`llama-3.3-70b-versatile`) | LLM Cognition | Evaluates nuanced contextual strength of top candidates with heuristic fallback |
| **NIYUKTI Copilot** | Groq REST API (`llama-3.1-8b-instant`) | LLM Cognition | Interactive recruiter chat, outreach drafts, and upskilling roadmaps |

---

## 6. Explainable Ranking (XAI)

Candidates are scored using a transparent 6-factor formula normalized from `0` to `100`:

$$\text{FinalScore} = (w_s \cdot S + w_e \cdot E + w_t \cdot T + w_d \cdot D + w_b \cdot B + w_l \cdot L) \times \prod \text{Multipliers}$$

### Component Weights
- **Skills Match (30%):** Weighted combination of categorized technical skill coverage and direct keyword matches. Includes a dedicated search/retrieval boost for relevant roles.
- **Experience Match (20%):** Proportional alignment of verified years of experience against role requirements.
- **Semantic Overlap (15%):** TF-IDF cosine similarity capturing domain relevance beyond raw keyword exact matches.
- **Education Tier (15%):** Honors advanced STEM degrees (Masters, PhD) and tier-1 institutions.
- **Behavioral Signals (10%):** Engagement signals from the Redrob platform (profile completeness, recruiter response rate, open-to-work flag, GitHub activity).
- **Location & Preference (10%):** Remote, Hybrid, or Onsite alignment with geographic preferences.

### Deterministic Disqualifier Penalties
- **Consulting-Only Tenure:** `-10%` penalty (`0.90x`) if candidate career history reflects exclusively short-term IT consulting contracts for product roles.
- **Title Chasing / High Churn:** `-5%` penalty (`0.95x`) if average job tenure across positions is under 15 months.
- **AI Wrapper Risk:** `-10%` penalty (`0.90x`) if listing generative wrappers without fundamental ML frameworks (PyTorch, TensorFlow, FAISS).

Every candidate detail view transparently displays exact matched skills, missing skills, and penalty reasons.

---

## 7. Candidate Matching

NIYUKTI's two-stage matching pipeline ensures sub-second retrieval over 100,001 candidates:
1. **Stage 1 (SQL & Heuristic Filtering):** Indexed column scans on title, experience, work mode, and primary skills narrow 100k+ candidates down to the relevant candidate pool.
2. **Stage 2 (Calibrated Scoring):** Evaluates multi-attribute weights and persists rank snapshots in the database.
3. **Stage 3 (LLM Rerank Cohort):** Top applicants can optionally be dispatched to Groq for qualitative re-scoring.

---

## 8. Skill-Gap Analysis

The Skill-Gap module enables recruiters to assess candidate growth potential:
- **Verified Proficiencies:** Skills extracted and verified from career history.
- **Mandatory Role Gaps:** Essential qualifications missing from the candidate's profile.
- **Recommended Development Areas:** Step-by-step guidance on adjacent technologies required to bridge the qualification gap.

---

## 9. Recruiter Copilot

The **NIYUKTI Copilot** is a contextual recruiter assistant:
- **Candidate-in-the-Loop:** Ingests the candidate's actual profile, years of experience, current title, and company history alongside job parameters.
- **Outreach Email Generation:** Generates professional outreach emails tailored to the specific role and candidate achievements.
- **Upskilling Roadmaps:** Outlines estimated durations and hands-on projects for bridging skill deltas.
- **Resilient Fallback:** If external LLM APIs are unreachable or unconfigured, the system automatically uses verified deterministic outreach templates.

---

## 10. Technology Stack

- **Frontend:** Vanilla HTML5, Vanilla JavaScript (ES6+), Tailwind CSS (CDN with custom Material Design 3 tokens), Google Fonts (Inter & Geist), Google Material Symbols.
- **Backend API:** Python 3.11+, FastAPI (ASGI), Uvicorn, Pydantic v2.
- **Database & ORM:** SQLAlchemy 2.0 with SQLite (local development) and PostgreSQL (production on Render).
- **Machine Learning & NLP:** Scikit-learn (TF-IDF vectorization), NumPy, SciPy, python-docx.
- **Large Language Models:** Groq Cloud API (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`).
- **Deployment & Hosting:** Vercel (static edge hosting + `/api/*` rewrite proxy), Render (FastAPI web service).

---

## 11. Local Setup

### Prerequisites
- Python 3.11 or higher
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/maitray-agrawal/NIYUKTI.git
   cd NIYUKTI
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to configure your `GROQ_API_KEY` (optional for local heuristic testing).

5. **Start the backend development server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will be available at `http://127.0.0.1:8000` with interactive Swagger docs at `/docs`.

6. **Open the frontend:**
   Open `frontend_screens/index.html` or `frontend_screens/dashboard.html` directly in your browser, or serve using any static server (e.g., VS Code Live Server or `npx serve frontend_screens`).

---

## 12. Environment Variables

| Variable | Description | Required | Default |
|:---|:---|:---:|:---|
| `DATABASE_URL` | SQLAlchemy connection string (SQLite or PostgreSQL) | No | `sqlite:///./data/talentmind.db` |
| `GROQ_API_KEY` | Groq Cloud API key for LLM reranker, JD parser, and Copilot | No | None (heuristic fallback active) |
| `FRONTEND_URL` | Allowed frontend domain for CORS headers | No | `http://localhost:3000` |
| `PORT` | Listening port for production server | No | `8000` |

---

## 13. Deployment

### Render (Backend & PostgreSQL)
1. Link your GitHub repository in Render.
2. Create a **Web Service** using the settings in `render.yaml`:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
3. Add environment variables in Render:
   - `DATABASE_URL`: Your Render PostgreSQL internal connection string.
   - `GROQ_API_KEY`: Your Groq Cloud API key.
   - `FRONTEND_URL`: Your Vercel domain (`https://talentmindai-app.vercel.app`).

### Vercel (Frontend)
1. Import the repository into Vercel.
2. Set the **Root Directory** to `frontend_screens`.
3. Vercel automatically reads `vercel.json` to proxy `/api/*` and `/health` requests to your live Render backend URL.
4. Clean URLs are enabled (`/dashboard` serves `dashboard.html`).

---

## 14. API Documentation

Interactive OpenAPI documentation is generated automatically by FastAPI:
- **Swagger UI:** `https://your-backend-url/docs`
- **ReDoc:** `https://your-backend-url/redoc`

Key API routes include:
- `GET /health` & `GET /api/health`: Database and Groq status probe
- `GET /api/candidates/?limit=20&offset=0`: Paginated candidate retrieval
- `GET /api/candidates/stats`: Global talent pool aggregate metrics
- `POST /api/jobs/analyze`: Job description parsing from text or `.docx`
- `POST /api/ranking/rank/{job_id}`: Deterministic heuristic ranking
- `POST /api/ranking/rerank/{job_id}`: Groq LLM reranking
- `POST /api/copilot/chat`: Contextual recruiter copilot
- `POST /api/submission/generate`: Export official Hack2Skill `submission.csv`

See [`API_AUDIT.md`](file:///d:/TalentMindAI/API_AUDIT.md) for the complete endpoint inventory.

---

## 15. Testing

Execute the test suite using `pytest`:

```bash
pytest backend/tests/test_backend.py backend/tests/test_ranking_engine.py backend/tests/test_submission.py backend/tests/test_ingestion.py backend/tests/test_jd_intelligence.py -v
```

All 27 backend unit and integration tests pass cleanly:
- `test_backend.py`: Candidate CRUD, Job CRUD, Ranking, Copilot chat, and JD Analyzer (6/6 PASS)
- `test_ranking_engine.py`: Multi-candidate heuristic ranking and limit validation (6/6 PASS)
- `test_submission.py`: Hack2Skill submission ordering and schema verification (1/1 PASS)
- `test_ingestion.py`: Streaming dataset ingestion and stats queries (3/3 PASS)
- `test_jd_intelligence.py`: Document parsing and section extraction (11/11 PASS)

See [`DEPLOYMENT_VERIFICATION.md`](file:///d:/TalentMindAI/DEPLOYMENT_VERIFICATION.md) for the full verification matrix.

---

## 16. Project Structure

```text
TalentMindAI/                          # Repository Root (ASTRA / NIYUKTI)
│
├── backend/
│   ├── app/
│   │   ├── models/                    # SQLAlchemy models (Candidate, Job, Ranking, AuditLog)
│   │   ├── routes/                    # FastAPI endpoints (candidates, jobs, ranking, copilot, submission)
│   │   ├── schemas/                   # Pydantic data schemas
│   │   ├── services/                  # Business logic (ranker, groq_reranker, copilot, ingestion)
│   │   ├── config.py                  # Environment & scoring weight configuration
│   │   ├── database.py                # Engine and session creation
│   │   └── main.py                    # FastAPI entrypoint, CORS, startup lifecycle
│   │
│   ├── tests/                         # Pytest test suite
│   ├── evaluate_ranking.py            # Ranking engine benchmark script
│   ├── generate_submission.py         # Standalone submission generator
│   ├── validate_submission.py         # Official Hack2Skill submission validator
│   └── requirements.txt               # Backend dependencies
│
├── frontend_screens/                  # Static frontend served by Vercel
│   ├── index.html                     # NIYUKTI Executive Portal & navigation launchpad
│   ├── dashboard.html                 # Executive recruitment command center
│   ├── candidate_search.html          # Candidate explorer & multi-filter search
│   ├── candidate_ranking.html         # Explainable ranking & reranking console
│   ├── candidate_details.html         # Candidate profile & XAI breakdown
│   ├── candidate_comparison.html      # Side-by-side candidate comparison matrix
│   ├── skill_gap_analysis.html        # Skill gap breakdown & development areas
│   ├── recruiter_copilot.html         # NIYUKTI conversational recruiter copilot
│   ├── settings.html                  # System settings & team permissions
│   ├── integration.js                 # Global API integration, navigation, and health monitor
│   ├── favicon.svg                    # Geometric NIYUKTI brand mark
│   └── vercel.json                    # Vercel proxy configuration & caching headers
│
├── docs/                              # System documentation & challenge benchmarks
├── .env.example                       # Documented environment variable template
├── .gitignore                         # Git hygiene rules
├── render.yaml                        # Render blueprint configuration
├── runtime.txt                        # Python 3.11.9 runtime declaration
├── submission.csv                     # Hack2Skill challenge output
├── NIYUKTI_MIGRATION_AUDIT.md         # Full repository migration audit
├── API_AUDIT.md                       # Comprehensive API inventory
├── DEPLOYMENT_VERIFICATION.md         # Deployment readiness verification report
└── README.md                          # Primary platform documentation
```

---

## 17. Limitations

- **Dataset Scale in Memory:** Batch processing 100,000+ candidates concurrently requires bounded queries (`yield_per` or pagination) to avoid memory saturation on constrained tiers.
- **LLM Rate Limits:** External Groq API calls are subject to provider rate limits (TPM/RPM); the platform mitigates this with exponential backoff and deterministic heuristic fallbacks.
- **Local SQLite Locking:** SQLite does not support high concurrency write transactions; PostgreSQL must be used for production deployments.

---

## 18. Future Scope

- **Asynchronous Task Workers:** Implement Celery or Redis Queue for decoupling heavy background batch ranking tasks from HTTP request lifecycles.
- **Vector Database Integration:** Incorporate Qdrant or pgvector for native dense semantic embeddings alongside sparse TF-IDF.
- **Automated Interview Scheduling:** Integrate calendar providers directly into the NIYUKTI Copilot workflow.
- **Bias Auditing Tooling:** Additional statistical demographic parity analysis across candidate pools.