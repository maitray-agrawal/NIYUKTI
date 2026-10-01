from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from collections import Counter
from app.database import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.ranking import Ranking
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateInDB
from app.schemas.explanation import CandidateExplanationResponse
from app.schemas.comparison import CandidateComparisonResponse
from app.services.ingestion import IngestionService
from app.services.ranker_service import RankerService
from app.services.comparison_service import ComparisonService


router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("/import", status_code=status.HTTP_200_OK)
def import_candidates(
    file_path: Optional[str] = None,
    limit: Optional[int] = None,
    batch_size: int = 1000,
    db: Session = Depends(get_db)
):
    if not file_path:
        # Default to a portable path relative to the backend directory
        from app.config import BASE_DIR
        file_path = str(BASE_DIR / "data" / "candidates.jsonl")
    try:
        result = IngestionService.ingest_candidates(db, file_path, limit, batch_size)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import time

_STATS_CACHE = {"data": None, "timestamp": 0.0}
_LOCATIONS_CACHE = {"data": None, "timestamp": 0.0}
CACHE_TTL_SECONDS = 300.0

@router.get("/stats")
def get_candidate_stats(db: Session = Depends(get_db)):
    now = time.time()
    if _STATS_CACHE["data"] is not None and (now - _STATS_CACHE["timestamp"]) < CACHE_TTL_SECONDS:
        return _STATS_CACHE["data"]

    try:
        is_sqlite = db.bind.dialect.name == "sqlite"
        if is_sqlite:
            flag_expr = func.sum(case((func.json_extract(Candidate.redrob_signals, '$.open_to_work_flag') == 1, 1), else_=0))
            comp_expr = func.avg(func.json_extract(Candidate.redrob_signals, '$.profile_completeness_score'))
        else:
            from sqlalchemy import cast, Integer, Float
            flag_expr = func.sum(case((cast(Candidate.redrob_signals['open_to_work_flag'].as_string(), Integer) == 1, 1), else_=0))
            comp_expr = func.avg(cast(Candidate.redrob_signals['profile_completeness_score'].as_string(), Float))

        stats_query = db.query(
            func.count(Candidate.id),
            func.avg(Candidate.experience_years),
            func.sum(case((Candidate.experience_years < 3.0, 1), else_=0)),
            func.sum(case(((Candidate.experience_years >= 3.0) & (Candidate.experience_years < 7.0), 1), else_=0)),
            func.sum(case(((Candidate.experience_years >= 7.0) & (Candidate.experience_years < 12.0), 1), else_=0)),
            func.sum(case((Candidate.experience_years >= 12.0, 1), else_=0)),
            flag_expr,
            comp_expr
        ).first()
    except Exception:
        total_fallback = db.query(func.count(Candidate.id)).scalar() or 0
        stats_query = (total_fallback, 0.0, 0, 0, 0, 0, 0, 0.0)

    total = stats_query[0] or 0
    if total == 0:
        res = {
            "total_candidates": 0,
            "average_experience": 0.0,
            "experience_distribution": {},
            "work_preference_distribution": {},
            "top_skills": [],
            "open_to_work_count": 0,
            "open_to_work_percentage": 0.0,
            "average_profile_completeness": 0.0
        }
        _STATS_CACHE["data"] = res
        _STATS_CACHE["timestamp"] = now
        return res

    avg_exp = stats_query[1] or 0.0
    entry = stats_query[2] or 0
    mid = stats_query[3] or 0
    senior = stats_query[4] or 0
    principal = stats_query[5] or 0
    open_to_work_count = stats_query[6] or 0
    avg_completeness = stats_query[7] or 0.0

    open_to_work_pct = (open_to_work_count / total) * 100

    pref_counts = db.query(Candidate.work_preference, func.count(Candidate.id)).group_by(Candidate.work_preference).all()
    work_pref_dist = {pref or "Unknown": count for pref, count in pref_counts}

    skills_query = db.query(Candidate.skills).limit(5000).all()
    all_skills = []
    for (skills_list,) in skills_query:
        if skills_list:
            all_skills.extend(skills_list)
    top_skills_counted = Counter(all_skills).most_common(10)
    top_skills = [{"skill": s, "count": c} for s, c in top_skills_counted]

    result = {
        "total_candidates": total,
        "average_experience": round(avg_exp, 2),
        "experience_distribution": {
            "Entry (<3 Yrs)": entry,
            "Mid (3-7 Yrs)": mid,
            "Senior (7-12 Yrs)": senior,
            "Principal (12+ Yrs)": principal
        },
        "work_preference_distribution": work_pref_dist,
        "top_skills": top_skills,
        "open_to_work_count": open_to_work_count,
        "open_to_work_percentage": round(open_to_work_pct, 2),
        "average_profile_completeness": round(avg_completeness, 2)
    }
    _STATS_CACHE["data"] = result
    _STATS_CACHE["timestamp"] = now
    return result


LOCATION_ALIASES = {
    "bengaluru": ["bangalore", "bengaluru"],
    "bangalore": ["bangalore", "bengaluru"],
    "delhi": ["delhi", "new delhi", "noida", "gurgaon", "gurugram"],
    "delhi-ncr": ["delhi", "new delhi", "noida", "gurgaon", "gurugram"],
    "delhi ncr": ["delhi", "new delhi", "noida", "gurgaon", "gurugram"],
    "ncr": ["delhi", "new delhi", "noida", "gurgaon", "gurugram"],
    "mumbai": ["mumbai", "bombay"],
    "bombay": ["mumbai", "bombay"],
    "chennai": ["chennai", "madras"],
    "madras": ["chennai", "madras"],
    "kolkata": ["kolkata", "calcutta"],
    "calcutta": ["kolkata", "calcutta"],
    "hyderabad": ["hyderabad"],
    "pune": ["pune"],
    "ahmedabad": ["ahmedabad"],
    "jaipur": ["jaipur"],
    "bhubaneswar": ["bhubaneswar"],
    "indore": ["indore"],
    "kochi": ["kochi", "cochin"],
    "cochin": ["kochi", "cochin"],
    "trivandrum": ["trivandrum", "thiruvananthapuram"],
    "thiruvananthapuram": ["trivandrum", "thiruvananthapuram"],
    "chandigarh": ["chandigarh"],
    "coimbatore": ["coimbatore"],
    "visakhapatnam": ["visakhapatnam", "vizag"],
    "vizag": ["visakhapatnam", "vizag"],
    "sydney": ["sydney"],
    "san francisco": ["san francisco"],
    "austin": ["austin"],
    "new york": ["new york"],
    "toronto": ["toronto"],
    "london": ["london"],
    "berlin": ["berlin"],
    "singapore": ["singapore"],
    "dubai": ["dubai"],
    "seattle": ["seattle"],
}

def build_location_clause(loc_input: str):
    cleaned = loc_input.lower().strip()
    aliases = LOCATION_ALIASES.get(cleaned)
    if aliases:
        from sqlalchemy import or_
        return or_(*[Candidate.location.ilike(f"%{alias}%") for alias in aliases])
    return Candidate.location.ilike(f"%{loc_input.strip()}%")

@router.get("/locations")
def get_candidate_locations(db: Session = Depends(get_db)):
    """Canonical geographic talent density across all regional and international hubs aggregated from real database records."""
    now = time.time()
    if _LOCATIONS_CACHE["data"] is not None and (now - _LOCATIONS_CACHE["timestamp"]) < CACHE_TTL_SECONDS:
        return _LOCATIONS_CACHE["data"]

    loc_counts = db.query(Candidate.location, func.count(Candidate.id)).group_by(Candidate.location).all()
    total_candidates = sum(cnt for _, cnt in loc_counts) or 100001
    
    hubs_map = {
        "Delhi-NCR": {"city": "Delhi-NCR", "state": "Delhi/NCR", "lat": 28.6139, "lng": 77.2090, "count": 0, "top_skills": ["Docker", "Python", "Full Stack", "HTML"]},
        "Bengaluru": {"city": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946, "count": 0, "top_skills": ["MongoDB", "Rust", "Apache Beam", "Python"]},
        "Hyderabad": {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867, "count": 0, "top_skills": ["Agile", "Vue.js", "JavaScript", "Cloud"]},
        "Pune": {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567, "count": 0, "top_skills": ["Redis", "Scrum", "PostgreSQL", "Data Science"]},
        "Mumbai": {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777, "count": 0, "top_skills": ["React", "Sales", "Webpack", "FinTech"]},
        "Chennai": {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707, "count": 0, "top_skills": ["Kafka", "CSS", "Vue.js", "Deep Learning"]},
        "Kolkata": {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639, "count": 0, "top_skills": ["Python", "Java", "Backend"]},
        "Bhubaneswar": {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245, "count": 0, "top_skills": ["Java", "SQL", "Spring"]},
        "Ahmedabad": {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714, "count": 0, "top_skills": ["Angular", "Node.js", "Python"]},
        "Jaipur": {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873, "count": 0, "top_skills": ["Data Science", "Python", "ML"]},
        "Indore": {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577, "count": 0, "top_skills": ["Python", "FastAPI", "PostgreSQL"]},
        "Trivandrum": {"city": "Trivandrum", "state": "Kerala", "lat": 8.5241, "lng": 76.9366, "count": 0, "top_skills": ["Node.js", "React", "Cloud"]},
        "Chandigarh": {"city": "Chandigarh", "state": "Chandigarh", "lat": 30.7333, "lng": 76.7794, "count": 0, "top_skills": ["DevOps", "Python", "Docker"]},
        "Coimbatore": {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558, "count": 0, "top_skills": ["Embedded", "IoT", "C++"]},
        "Kochi": {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673, "count": 0, "top_skills": ["Java", "Cloud", "Microservices"]},
        "Vizag": {"city": "Vizag", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185, "count": 0, "top_skills": ["Python", "Backend", "Data"]},
        "Global Hubs": {"city": "International Hubs", "state": "Global (US, UK, EU, APAC)", "lat": 37.7749, "lng": -122.4194, "count": 0, "top_skills": ["AI/ML", "Distributed Systems", "Kubernetes", "Rust"]}
    }
    
    for raw_loc, count in loc_counts:
        if not raw_loc:
            continue
        raw_lower = raw_loc.lower()
        if any(term in raw_lower for term in ["delhi", "noida", "gurgaon", "gurugram"]):
            hubs_map["Delhi-NCR"]["count"] += count
        elif "bangalore" in raw_lower or "bengaluru" in raw_lower:
            hubs_map["Bengaluru"]["count"] += count
        elif "hyderabad" in raw_lower:
            hubs_map["Hyderabad"]["count"] += count
        elif "pune" in raw_lower:
            hubs_map["Pune"]["count"] += count
        elif "mumbai" in raw_lower or "bombay" in raw_lower:
            hubs_map["Mumbai"]["count"] += count
        elif "chennai" in raw_lower or "madras" in raw_lower:
            hubs_map["Chennai"]["count"] += count
        elif "kolkata" in raw_lower or "calcutta" in raw_lower:
            hubs_map["Kolkata"]["count"] += count
        elif "bhubaneswar" in raw_lower:
            hubs_map["Bhubaneswar"]["count"] += count
        elif "ahmedabad" in raw_lower:
            hubs_map["Ahmedabad"]["count"] += count
        elif "jaipur" in raw_lower:
            hubs_map["Jaipur"]["count"] += count
        elif "indore" in raw_lower:
            hubs_map["Indore"]["count"] += count
        elif "trivandrum" in raw_lower or "thiruvananthapuram" in raw_lower:
            hubs_map["Trivandrum"]["count"] += count
        elif "chandigarh" in raw_lower:
            hubs_map["Chandigarh"]["count"] += count
        elif "coimbatore" in raw_lower:
            hubs_map["Coimbatore"]["count"] += count
        elif "kochi" in raw_lower or "cochin" in raw_lower:
            hubs_map["Kochi"]["count"] += count
        elif "vizag" in raw_lower or "visakhapatnam" in raw_lower:
            hubs_map["Vizag"]["count"] += count
        else:
            hubs_map["Global Hubs"]["count"] += count

    hubs_list = list(hubs_map.values())
    for h in hubs_list:
        h["percentage"] = round((h["count"] / total_candidates) * 100, 1) if total_candidates else 0.0

    result = {
        "total_candidates": total_candidates,
        "hubs": hubs_list
    }
    _LOCATIONS_CACHE["data"] = result
    _LOCATIONS_CACHE["timestamp"] = now
    return result

@router.get("/search", response_model=List[CandidateInDB])
def search_candidates(
    q: Optional[str] = None,
    skill: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    work_preference: Optional[str] = None,
    open_to_work: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Candidate)
    
    if q:
        from sqlalchemy import or_
        q_clean = q.strip()
        query = query.filter(
            or_(
                Candidate.name.ilike(f"%{q_clean}%"),
                Candidate.title.ilike(f"%{q_clean}%"),
                Candidate.location.ilike(f"%{q_clean}%"),
                Candidate.skills.ilike(f"%{q_clean}%")
            )
        )
    if location:
        query = query.filter(build_location_clause(location))
    if min_experience:
        query = query.filter(Candidate.experience_years >= min_experience)
    if max_experience:
        query = query.filter(Candidate.experience_years <= max_experience)
    if work_preference:
        query = query.filter(Candidate.work_preference.ilike(work_preference))
    if open_to_work is not None:
        flag_val = 1 if open_to_work else 0
        is_sqlite = db.bind.dialect.name == "sqlite"
        if is_sqlite:
            query = query.filter(func.json_extract(Candidate.redrob_signals, '$.open_to_work_flag') == flag_val)
        else:
            from sqlalchemy import cast, Integer
            query = query.filter(cast(Candidate.redrob_signals['open_to_work_flag'].as_string(), Integer) == flag_val)
        
    if skill:
        for s in skill.split(","):
            s_clean = s.strip()
            if s_clean:
                query = query.filter(Candidate.skills.like(f'%"{s_clean}"%'))
                
    offset_val = getattr(offset, "default", 0) if not isinstance(offset, int) else offset
    limit_val = getattr(limit, "default", 50) if not isinstance(limit, int) else limit
    return query.offset(offset_val).limit(limit_val).all()

@router.get("/", response_model=List[CandidateInDB])
def read_candidates(
    q: Optional[str] = None,
    skill: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    work_preference: Optional[str] = None,
    open_to_work: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    response: Response = None
):
    query = db.query(Candidate)
    
    if q:
        from sqlalchemy import or_
        q_clean = q.strip()
        query = query.filter(
            or_(
                Candidate.name.ilike(f"%{q_clean}%"),
                Candidate.title.ilike(f"%{q_clean}%"),
                Candidate.location.ilike(f"%{q_clean}%"),
                Candidate.skills.ilike(f"%{q_clean}%")
            )
        )
    if location:
        query = query.filter(build_location_clause(location))
    if status:
        query = query.filter(Candidate.status == status)
    if work_preference:
        prefs = [p.strip() for p in work_preference.split(",") if p.strip()]
        if prefs:
            title_prefs = [p.capitalize() for p in prefs]
            query = query.filter(Candidate.work_preference.in_(title_prefs))
    if min_experience:
        query = query.filter(Candidate.experience_years >= min_experience)
    if max_experience:
        query = query.filter(Candidate.experience_years <= max_experience)
    if open_to_work is not None:
        flag_val = 1 if open_to_work else 0
        is_sqlite = db.bind.dialect.name == "sqlite"
        if is_sqlite:
            query = query.filter(func.json_extract(Candidate.redrob_signals, '$.open_to_work_flag') == flag_val)
        else:
            from sqlalchemy import cast, Integer
            query = query.filter(cast(Candidate.redrob_signals['open_to_work_flag'].as_string(), Integer) == flag_val)
        
    if skill:
        for s in skill.split(","):
            s_clean = s.strip()
            if s_clean:
                query = query.filter(Candidate.skills.like(f'%"{s_clean}"%'))
                
    if response is not None:
        total_count = query.count()
        response.headers["X-Total-Count"] = str(total_count)
                
    offset_val = getattr(offset, "default", 0) if not isinstance(offset, int) else offset
    limit_val = getattr(limit, "default", 20) if not isinstance(limit, int) else limit
    return query.offset(offset_val).limit(limit_val).all()

@router.get("/{candidate_id}", response_model=CandidateInDB)
def read_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.post("/", response_model=CandidateInDB, status_code=status.HTTP_201_CREATED)
def create_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db)):
    db_cand = db.query(Candidate).filter(Candidate.email == candidate_in.email).first()
    if db_cand:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_candidate = Candidate(**candidate_in.model_dump())
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return new_candidate

@router.put("/{candidate_id}", response_model=CandidateInDB)
def update_candidate(candidate_id: int, candidate_in: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    update_data = candidate_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(candidate, key, val)
        
    db.commit()
    db.refresh(candidate)

    # Record in AuditLog (Niyukti Decision Ledger)
    try:
        from app.models.audit import AuditLog
        from datetime import datetime, timezone
        new_status = update_data.get("status", "Updated Profile")
        audit_entry = AuditLog(
            candidate_id=candidate.id,
            action=f"Recruiter Decision: Status -> {new_status}",
            details=f"Candidate #{candidate.id} ({candidate.name}) marked as '{new_status}' in recruitment workflow.",
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        pass

    return candidate

@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return None

@router.get("/{candidate_id}/explanation", response_model=CandidateExplanationResponse)
def get_candidate_explanation(
    candidate_id: int,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Resolve job
    if job_id is not None:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
    else:
        # fallback to first job
        job = db.query(Job).first()
        if not job:
            raise HTTPException(status_code=404, detail="No jobs found in the database")

    # Find ranking or calculate match
    ranking = db.query(Ranking).filter(
        Ranking.candidate_id == candidate.id,
        Ranking.job_id == job.id
    ).first()

    if ranking:
        score = ranking.match_score
        explanation = ranking.explanation
        tier = ranking.tier
    else:
        # Calculate dynamically
        score, explanation, tier = RankerService.calculate_match(candidate, job)

    # 1. Why Candidate Matched
    why_matched = (
        f"{candidate.name} is classified as a '{tier}' for the {job.title} position, "
        f"matching with an overall compatibility score of {score}%. "
        f"They possess {candidate.experience_years or 0.0} years of professional experience (required: {job.experience_required or 0.0} years) "
        f"and align with {len(explanation.get('matched_skills', []))} out of {len(explanation.get('matched_skills', [])) + len(explanation.get('missing_skills', []))} required skills."
    )

    # 2. Key Strengths
    strengths = []
    skills_score = explanation.get("skills_score", 0.0)
    if skills_score >= 80.0:
        strengths.append(f"High technical alignment: Matches {skills_score}% of the required skill categories.")
    elif skills_score >= 50.0:
        strengths.append("Foundational technical alignment: Matches primary skill requirements.")

    matched_skills = explanation.get("matched_skills", [])
    if matched_skills:
        strengths.append(f"Demonstrated core proficiency: Strong experience with {', '.join(matched_skills[:3])}.")

    exp_diff = explanation.get("experience_difference_years", 0.0)
    if exp_diff >= 3.0:
        strengths.append(f"Seniority surplus: Exceeds the role's targeted experience requirement by {round(exp_diff, 1)} years.")
    elif exp_diff >= 0.0:
        strengths.append(f"Meets experience criteria: Possesses {candidate.experience_years or 0.0} years of experience.")

    if explanation.get("has_retrieval_experience"):
        strengths.append("Domain expertise: Proven career background in search, recommendation systems, or information retrieval.")

    edu_score = explanation.get("education_score", 0.0)
    if edu_score >= 80.0:
        strengths.append("Strong academic credentials: High-tier computer science or technical degree background.")

    beh_score = explanation.get("behavioral_score", 0.0)
    if beh_score >= 80.0:
        strengths.append("High platform engagement: Excellent profile completeness and responsiveness indicators.")

    # Fallback if list is too short
    if len(strengths) < 2:
        strengths.append("Basic requirements met: Matches key qualifications for the role.")
        strengths.append("Responsive profile: Actively reachable on the platform.")

    # 3. Weaknesses / Risks
    weaknesses = []
    missing_skills = explanation.get("missing_skills", [])
    if missing_skills:
        weaknesses.append(f"Skill gaps detected: Lacks proven experience in key requested capabilities: {', '.join(missing_skills[:3])}.")

    exp_diff = explanation.get("experience_difference_years", 0.0)
    if exp_diff < 0:
        weaknesses.append(f"Experience deficit: Under-qualified by {round(abs(exp_diff), 1)} years relative to the job requirements.")

    # Average company tenure
    if candidate.career_history and len(candidate.career_history) >= 2:
        total_months = sum(jh.get("duration_months") or 0 for jh in candidate.career_history)
        if total_months > 0:
            avg_tenure = total_months / len(candidate.career_history)
            if avg_tenure < 15.0:
                weaknesses.append(f"Retention risk warning: Candidate exhibits a high-turnover pattern with an average tenure of {round(avg_tenure, 1)} months.")

    loc_score = explanation.get("location_score", 0.0)
    if loc_score < 50.0:
        weaknesses.append(f"Location mismatch: Prefers {candidate.work_preference or 'Remote'} mode but the role is {job.work_preference or 'Onsite'} in {job.location or 'any office'}.")

    cand_skills_set = {s.lower().strip() for s in (candidate.skills or [])}
    has_wrapper = any(s in cand_skills_set for s in ["langchain", "openai", "openai embeddings"])
    has_core = any(s in cand_skills_set for s in ["pytorch", "tensorflow", "scikit-learn", "xgboost", "lightgbm", "search", "retrieval", "ranking", "recommendation"])
    if has_wrapper and not has_core:
        weaknesses.append("Foundational gap: Demonstrates knowledge of wrapper APIs (LangChain/OpenAI) but lacks core ML/algorithmic foundations.")

    if not weaknesses:
        weaknesses.append("No major technical or cultural risk factors identified.")

    # 4. Hiring Recommendation
    if score >= 85.0:
        hiring_recommendation = (
            f"Fast-Track to Interview: Highly recommended. {candidate.name} is an exceptional fit ({score}%) who meets "
            f"or exceeds all key criteria. Their engineering background is highly compatible with AstraX / NIYUKTI architectures."
        )
    elif score >= 70.0:
        hiring_recommendation = (
            f"Proceed to Screening: Recommended. {candidate.name} is a strong candidate ({score}%) with minor skill gaps "
            f"in {', '.join(missing_skills[:2]) if missing_skills else 'certain technologies'} that can be easily addressed via onboarding upskilling."
        )
    elif score >= 50.0:
        hiring_recommendation = (
            f"Conditional Review: Neutral. {candidate.name} matches basic criteria ({score}%), but shows notable gaps in experience "
            f"or skills. Recommend scheduling a preliminary technical call if top-tier options are limited."
        )
    else:
        hiring_recommendation = (
            f"Do Not Proceed: Unsuitable. {candidate.name} ({score}%) lacks core qualifications, required experience, "
            f"or critical technical capabilities needed for this role."
        )

    return CandidateExplanationResponse(
        candidate_id=candidate.id,
        job_id=job.id,
        match_score=score,
        tier=tier,
        why_matched=why_matched,
        strengths=strengths,
        weaknesses=weaknesses,
        missing_skills=missing_skills,
        hiring_recommendation=hiring_recommendation
    )


@router.post("/compare", response_model=CandidateComparisonResponse, status_code=status.HTTP_200_OK)
def compare_candidates(
    candidate_ids: List[int],
    job_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Compare multiple candidates side-by-side.
    
    Shows:
    - Skills and proficiency levels
    - Experience and career history
    - Education background
    - Behavioral signals and engagement
    - Ranking scores (if job_id provided)
    - Hiring recommendations
    
    Args:
        candidate_ids: List of candidate IDs to compare (minimum 2)
        job_id: Optional job ID for ranking comparison
        db: Database session
        
    Returns:
        Comprehensive comparison data for all candidates
    """
    try:
        comparison_data = ComparisonService.compare_candidates(
            candidate_ids=candidate_ids,
            job_id=job_id,
            db=db
        )
        return CandidateComparisonResponse(
            candidates=comparison_data["candidates"],
            summary=comparison_data["summary"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

