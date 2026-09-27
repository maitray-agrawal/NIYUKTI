# NIYUKTI

## AI-Powered Talent Intelligence & Recruitment Platform

**NIYUKTI** is an AI-powered talent intelligence platform designed to help recruiters discover, evaluate, compare, and understand candidates through intelligent candidate search, explainable ranking, skill-gap analysis, and recruiter assistance.

Built under the **ASTRA** umbrella, NIYUKTI focuses on making recruitment decisions more structured, explainable, and data-driven — without reducing candidates to a single opaque score.

---

### Live Application

**Production Frontend:**
[https://astra-niyukti.vercel.app/](https://astra-niyukti.vercel.app/)

The frontend is deployed on Vercel and communicates with the production API through the application's `/api/*` routing layer.

---

## About NIYUKTI

NIYUKTI comes from the Sanskrit word **नियुक्ति (Niyukti)**, referring to appointment, employment, placement, or engagement.

The name reflects the platform's core purpose:
> **Connecting the right talent with the right opportunity through intelligent, explainable recruitment intelligence.**

NIYUKTI combines structured candidate data, job requirements, deterministic scoring, AI-assisted analysis, and recruiter workflows into a unified recruitment intelligence platform.

---

## Key Capabilities

### Candidate Intelligence
Search and explore candidates using structured attributes and recruitment-relevant signals:
- Candidate discovery
- Skill-based search
- Experience-based filtering
- Candidate profiles
- Candidate explanations
- Structured candidate intelligence

### Explainable Candidate Ranking
Rank candidates against specific job requirements using a transparent scoring methodology. The ranking system considers:
- Skills compatibility
- Experience relevance
- Job requirement matching
- Candidate-job compatibility

Rather than presenting only a final score, NIYUKTI exposes supporting signals behind the ranking.

### Skill Gap Analysis
Identify the difference between:
```
Required Skills ──► Candidate Skills ──► Matched Skills ──► Missing / Gap Skills ──► Match Analysis
```
This allows recruiters to distinguish between candidates who fully satisfy a role and candidates who may require additional training or upskilling.

### Candidate Comparison
Compare multiple candidates side-by-side using consistent recruitment criteria:
- Overall matching
- Skills breakdown
- Experience levels
- Skill gaps
- Relevant candidate signals
- Ranking information

### Recruiter Copilot
NIYUKTI includes an AI-assisted recruiter copilot for recruitment workflows:
- Candidate-related questions
- Recruitment analysis
- Candidate-job reasoning
- Outreach assistance
- Email drafting
- Recruiter workflow support

*AI-generated outputs are intended to assist recruiters rather than replace human decision-making.*

### Job Description Intelligence
Job descriptions can be processed to extract recruitment-relevant information and convert unstructured requirements into structured signals for downstream candidate analysis.

### Submission & Evaluation Pipeline
The platform also includes a structured submission-generation workflow for candidate-ranking outputs and validation of generated recruitment datasets.

---

## Product Architecture

```
┌──────────────────────────────────────────────┐
│                   NIYUKTI                    │
│   AI-Powered Talent Intelligence Platform    │
└──────────────────────┬───────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│    Candidate     │        │    Recruiter     │
│   Intelligence   │        │   Intelligence   │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
   ┌─────┴──────┐              ┌─────┴──────┐
   ▼            ▼              ▼            ▼
Search       Ranking       Skill Gap     Copilot
   │            │              │            │
   └────────────┴──────┬───────┴────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│               FastAPI Backend                │
│                API + Services                │
└──────────────────────┬───────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│    PostgreSQL    │        │   AI Services    │
│  Candidate Data  │        │   Groq / LLM     │
└──────────────────┘        └──────────────────┘
```

---

## Application Modules

| Module | Purpose |
|---|---|
| **Dashboard** | Recruitment intelligence overview and platform metrics |
| **Candidate Search** | Discover candidates using structured filters and signals |
| **Candidate Ranking** | Rank candidates against job requirements |
| **Candidate Details** | Inspect individual candidate intelligence |
| **Candidate Comparison** | Compare candidates side-by-side |
| **Skill Gap Analysis** | Identify missing and matched skills |
| **Recruiter Copilot** | AI-assisted recruitment workflows |
| **Settings** | Platform and recruiter configuration |
| **Submission** | Generate and validate structured candidate outputs |

---

## Technology Stack

### Frontend
- HTML5, CSS3, Modern JavaScript
- Responsive dashboard UI
- Dynamic REST API integration via `/api/...`
- Vercel deployment with root directory `frontend_screens`
*The current frontend intentionally uses a lightweight web architecture rather than introducing a heavyweight framework where it is not required.*

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy ORM
- Pydantic models
- Modular service architecture

### Database
- PostgreSQL (Production on Render)
- SQLAlchemy ORM
- JSON-based candidate signals (`redrob_signals`)
- SQLite-compatible development configuration

### AI / Intelligence Layer
- Groq API (`llama-3.3-70b-versatile` / fallback)
- LLM-assisted job-description intelligence
- LLM-assisted recruiter workflows
- AI reranking and explainable candidate analysis

### Deployment
- **Frontend:** Vercel (`https://astra-niyukti.vercel.app/`)
- **Backend:** Render (`https://talentmindai-rgar.onrender.com/`)
- **Database:** PostgreSQL on Render
- Environment-based configuration

---

## Ranking & Explainability

NIYUKTI is designed around the principle that recruitment intelligence should be interpretable. Instead of treating an AI-generated score as the final answer, the platform exposes the underlying recruitment signals:

```
Job Description
      │
      ▼
Requirement Extraction
      │
      ▼
Candidate Retrieval
      │
      ▼
Structured Matching
      │
      ▼
Candidate Scoring
      │
      ▼
AI-assisted Reranking
      │
      ▼
Explainable Results
      │
      ▼
Recruiter Decision
```

This creates a clearer relationship between:
**Job Requirements → Candidate Evidence → Matching Signals → Recommendation**

### Explainable AI
NIYUKTI is designed to answer not only *"Who is the strongest candidate?"* but also *"Why does this candidate match the role?"*

Candidate explanations surface:
- Matched skills
- Missing skills
- Experience relevance
- Job-specific signals
- Matching evidence
- Skill gaps
- Ranking context

---

## AI Recruiter Copilot

The **Recruiter Copilot** acts as an AI assistant inside the recruitment workflow:

```
Recruiter
   │
   ├── Select Candidate
   ├── Select Job
   └── Ask Copilot
         │
         ▼
   Context Assembly
         │
         ▼
    AI Analysis
         │
         ▼
 Structured Response
         │
         ▼
  Recruiter Review
```

Example use cases include:
- Drafting candidate outreach and personalized emails
- Understanding candidate-job fit
- Identifying skill gaps and interview recommendations
- Summarizing candidate experience and redrob signals
- Generating recruitment communication

---

## Data Flow

```
Candidate Dataset
      │
      ▼
Data Ingestion
      │
      ▼
   Database
      │
      ▼
Candidate Retrieval ───────┐
      │                    │
      ▼                    ▼
Job Requirements    Candidate Signals
      │                    │
      └─────────┬──────────┘
                │
                ▼
         Matching Engine
                │
                ▼
         Ranking Engine
          ┌─────┴─────┐
          ▼     ▼     ▼
    Ranking    XAI  Skill Gap
          └─────┬─────┘
                │
                ▼
           Recruiter UI
                │
                ▼
          Human Decision
```

---

## Scale

The platform's verification environment supports a candidate dataset of **100,001 candidate records**. The API and database layer were engineered for candidate aggregation, structured search, and retrieval at this scale.

---

## Testing

The backend includes automated tests covering core platform functionality:

```
27 passed, 0 failed — 100% pass rate
```

Covered test suites:
- Backend API (`test_backend.py`)
- Ranking Engine (`test_ranking_engine.py`)
- Submission Pipeline (`test_submission.py`)
- Data Ingestion (`test_ingestion.py`)
- Job Description Intelligence (`test_jd_intelligence.py`)

Run the test suite locally:
```bash
pytest backend/tests/test_backend.py \
       backend/tests/test_ranking_engine.py \
       backend/tests/test_submission.py \
       backend/tests/test_ingestion.py \
       backend/tests/test_jd_intelligence.py -v
```

---

## Project Structure

```
NIYUKTI/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── candidates.py
│   │   │   ├── ranking.py
│   │   │   ├── copilot.py
│   │   │   ├── submission.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── copilot_service.py
│   │   │   ├── groq_reranker.py
│   │   │   ├── groq_jd_service.py
│   │   │   └── ...
│   │   ├── config.py
│   │   ├── main.py
│   │   └── seed.py
│   └── tests/
├── frontend_screens/
│   ├── index.html
│   ├── dashboard.html
│   ├── candidate_search.html
│   ├── candidate_ranking.html
│   ├── candidate_details.html
│   ├── candidate_comparison.html
│   ├── skill_gap_analysis.html
│   ├── recruiter_copilot.html
│   ├── settings.html
│   ├── integration.js
│   ├── favicon.svg
│   └── vercel.json
├── render.yaml
├── .env.example
├── .gitignore
├── README.md
└── ...
```

---

## Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/maitray-agrawal/NIYUKTI.git
cd NIYUKTI
```

### 2. Create a Virtual Environment
**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file using `.env.example` as the reference:
```env
DATABASE_URL=sqlite:///./candidates.db
GROQ_API_KEY=your_groq_api_key_here
FRONTEND_URL=http://localhost:5500,https://astra-niyukti.vercel.app
```
*Never commit production secrets to Git.*

### 5. Start the Backend
```bash
uvicorn backend.app.main:app --reload
```
The API and OpenAPI docs will be available at `http://127.0.0.1:8000/docs`.

### 6. Run the Frontend
The frontend is a static application. Serve `frontend_screens/` using a local HTTP server:
```bash
python -m http.server 5500 --directory frontend_screens
```
Then navigate to `http://localhost:5500/` in your browser.

---

## Production Deployment

NIYUKTI uses a decoupled production deployment architecture:

```
GitHub (main)
   │
   ├──────────────► Vercel
   │                   │
   │                   ▼
   │             Static Frontend (frontend_screens/)
   │                   │
   │                   │  /api/* (Proxy rewrite)
   │                   ▼
   └──────────────► Render
                       │
                       ▼
                 FastAPI Backend
                       │
                       ▼
                 PostgreSQL DB
```

### Frontend
- **Platform:** Vercel
- **Root Directory:** `frontend_screens`
- This ensures Vercel deploys the static frontend directly rather than attempting to build Python backend code.

### API Routing
Frontend requests use relative API paths:
```javascript
const API_BASE = '/api';
```
Production `vercel.json` rewrites forward `/api/:path*` to the Render backend:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://talentmindai-rgar.onrender.com/api/:path*"
    }
  ]
}
```
This avoids hardcoding backend origins into frontend source code and maintains a clean contract.

---

## Security Considerations

NIYUKTI adheres to production security standards:
- **Environment-based secrets:** No credentials in source control.
- **Client safety:** No API keys exposed in frontend JavaScript.
- **No hardcoded local paths:** All routing is environment-driven.
- **HTTP security headers:** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`.
- **Controlled CORS:** Explicitly permits only known production and local development origins.
- **Dialect-safe queries:** Safe SQL execution across SQLite and PostgreSQL.

---

## API Design

The backend exposes clean RESTful API endpoints for recruitment workflows:
- `/health` and `/api/health` — System health and database connectivity
- `/api/candidates` — Candidate search, pagination, and signal filtering
- `/api/candidates/stats` — High-scale dataset metrics
- `/api/ranking/` — Deterministic and AI-reranked candidate matching
- `/api/ranking/skill-gap` — Detailed required vs. candidate skill difference
- `/api/copilot/chat` — Recruiter Copilot conversational assistant
- `/api/copilot/outreach` — Context-aware email drafting
- `/api/jobs` — Job description CRUD and AI analysis
- `/api/submission` — Submission CSV generation and evaluation

Interactive Swagger UI documentation is available at `/docs`.

---

## Design Principles

1. **01 — Evidence over opacity:** Recruitment recommendations should be supported by identifiable candidate signals.
2. **02 — Human-in-the-loop:** AI assists recruiters; final recruitment decisions remain with humans.
3. **03 — Structured intelligence:** Unstructured candidate and job information is converted into structured recruitment signals.
4. **04 — Modular architecture:** Search, ranking, explanation, skill-gap analysis, AI assistance, and data processing are independently organized.
5. **05 — Production readiness:** Designed with environment configuration, testing, deployment separation, API contracts, and security considerations in mind.

---

## Current Feature Status

| Capability | Status |
|---|---|
| Candidate Search | Production Ready |
| Candidate Ranking | Production Ready |
| Explainable Candidate Analysis | Production Ready |
| Skill Gap Analysis | Production Ready |
| Candidate Comparison | Production Ready |
| Recruiter Copilot | Production Ready |
| Job Description Intelligence | Production Ready |
| Submission Generation | Production Ready |
| PostgreSQL Support | Production Ready |
| Vercel Frontend Deployment | Production Ready |
| Render Backend Deployment | Production Ready |
| Automated Backend Tests | Passing (27/27) |

---

## ASTRA Product Family

NIYUKTI is part of a broader product naming architecture under **ASTRA**:

```
ASTRA
├── NIYUKTI
│   └── Talent Intelligence & Recruitment
├── KUBERSETU
│   └── Financial / Transaction Intelligence
└── Future Domain Products
```

The naming system uses concise Sanskrit-derived names to create a consistent identity across domain-specific AI systems.

---

## Why NIYUKTI?

Traditional recruitment platforms often separate:
`Search ──► Ranking ──► Candidate Analysis ──► Skill Gaps ──► Recruiter Communication`
into disconnected tools.

NIYUKTI brings these capabilities together:

```
                      NIYUKTI
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Discover          Evaluate        Understand
Candidate Search      Ranking         Skill Gaps
        └────────────────┼────────────────┘
                         │
                         ▼
                       Assist
                  Recruiter Copilot
                         │
                         ▼
                Human Decision-Making
```

The goal is to provide recruiters with a decision-support layer over candidate data.

---

## Roadmap

- Semantic candidate retrieval & vector-based matching
- Advanced RAG for recruitment intelligence
- Multi-agent recruiter workflows
- Interview intelligence & question generation
- Bias and fairness monitoring
- Recruiter analytics & workforce intelligence
- Automated talent-pipeline generation
- Enterprise role-based access control (RBAC)
- Audit logs and decision history

---

## Responsible AI

NIYUKTI is intended as a recruitment decision-support system. AI-generated outputs should be treated as recommendations or assistance rather than autonomous hiring decisions.

Recruiters should independently review:
- Candidate qualifications
- Relevant experience
- Skill evidence
- Job requirements
- AI-generated explanations
- Potential skill gaps

before making employment decisions. The system should not be used as the sole basis for hiring, rejection, or other consequential employment decisions.

---

## Project Status

NIYUKTI is deployed as a production-oriented AI recruitment intelligence platform with an independently deployed frontend and backend architecture.

- **Production Frontend:** [https://astra-niyukti.vercel.app/](https://astra-niyukti.vercel.app/)
- **Production Backend:** [https://talentmindai-rgar.onrender.com/](https://talentmindai-rgar.onrender.com/)
- **Canonical Repository:** [https://github.com/maitray-agrawal/NIYUKTI.git](https://github.com/maitray-agrawal/NIYUKTI.git)

---

## Author

**Maitray Agrawal**
B.Tech — Computer Science & Engineering (AI & ML)
Pimpri Chinchwad University, Pune

**Areas of Interest:**
Artificial Intelligence • Machine Learning • Generative AI • LLM Applications • Agentic AI • Data Science • Backend Engineering • AI Product Development

---

## License

This project is intended for educational, research, demonstration, and portfolio purposes unless otherwise specified by the repository owner.
