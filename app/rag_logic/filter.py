from app.core.logger import logger
from langchain_core.messages import HumanMessage
from sqlalchemy import text
from pydantic.config import ConfigDict

# ── DB helpers ──────────────────────────────────────────────────────────────


def get_valid_filter_values(db, user_id: str) -> dict:
    # skills and domain are PG arrays — need unnest() to get distinct values
    # Join resumes with user_resumes to filter by user_id
    return {
        "domains": [r[0] for r in db.execute(
            text("""
                SELECT DISTINCT unnest(r.domain) 
                FROM resumes r
                INNER JOIN user_resumes ur ON r.id = ur.resume_id
                WHERE ur.user_id = :user_id 
                AND r.domain IS NOT NULL
            """),
            {"user_id": user_id}
        ).fetchall()],

        "skills": [r[0] for r in db.execute(
            text("""
                SELECT DISTINCT unnest(r.skills) 
                FROM resumes r
                INNER JOIN user_resumes ur ON r.id = ur.resume_id
                WHERE ur.user_id = :user_id 
                AND r.skills IS NOT NULL
            """),
            {"user_id": user_id}
        ).fetchall()],

        "cities": [r[0] for r in db.execute(
            text("""
                SELECT DISTINCT r.city 
                FROM resumes r
                INNER JOIN user_resumes ur ON r.id = ur.resume_id
                WHERE ur.user_id = :user_id 
                AND r.city IS NOT NULL
            """),
            {"user_id": user_id}
        ).fetchall()],

        "states": [r[0] for r in db.execute(
            text("""
                SELECT DISTINCT r.state 
                FROM resumes r
                INNER JOIN user_resumes ur ON r.id = ur.resume_id
                WHERE ur.user_id = :user_id 
                AND r.state IS NOT NULL
            """),
            {"user_id": user_id}
        ).fetchall()],

        "experience": db.execute(
            text("""
                SELECT MIN(r.experience_years), MAX(r.experience_years) 
                FROM resumes r
                INNER JOIN user_resumes ur ON r.id = ur.resume_id
                WHERE ur.user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()
    }

# ── Dynamic tool factory ─────────────────────────────────────────────────────
# Rebuild the tool every query so enums always reflect current DB state




def make_filter_tool(valid: dict):
    from pydantic import BaseModel, Field
    from typing import List, Optional

    class CandidateFilter(BaseModel):
        model_config = ConfigDict(populate_by_name=True)
        
        domains:        List[str] = Field(..., description=f"Only pick from: {valid['domains']}")
        skills:         List[str] = Field(..., description=f"Only pick from: {valid['skills']}")
        cities:         List[str] = Field(..., description=f"Only pick from: {valid['cities']}")
        states:         List[str] = Field(..., description=f"Only pick from: {valid['states']}")
        experience_min: Optional[int] = Field(default=None, description="Minimum years of experience")
        experience_max: Optional[int] = Field(default=None, description="Maximum years of experience")
    return CandidateFilter

# ── Validation ───────────────────────────────────────────────────────────────

def validate_filters(raw_filters: dict, valid: dict) -> dict:
    valid_domains = set(valid["domains"])
    valid_skills  = set(valid["skills"])
    valid_cities  = set(valid["cities"])
    valid_states  = set(valid["states"])

    return {
        # filter_applied is ignored — it was only there to satisfy Cohere
        "domains":        [d for d in (raw_filters.get("domains")  or []) if d in valid_domains],
        "skills":         [s for s in (raw_filters.get("skills")   or []) if s in valid_skills],
        "cities":         [c for c in (raw_filters.get("cities")   or []) if c in valid_cities],
        "states":         [s for s in (raw_filters.get("states")   or []) if s in valid_states],
        "experience_min": raw_filters.get("experience_min"),
        "experience_max": raw_filters.get("experience_max"),
    }

# ── SQL builder ──────────────────────────────────────────────────────────────





def build_sql(filters: dict, user_id: str) -> tuple:
    # Start with user_resumes join to filter by user
    conditions = ["ur.user_id = :user_id"]
    params     = {"user_id": user_id}

    # Fix — cast Python list to PG array explicitly using ANY()
    if filters.get("domains"):
        # Expand list into named params for text() compatibility
        domain_params = {f"domain_{i}": v for i, v in enumerate(filters["domains"])}
        placeholders  = ",".join(f":domain_{i}" for i in range(len(filters["domains"])))
        conditions.append(f"r.domain && ARRAY[{placeholders}]::varchar[]")
        params.update(domain_params)

    if filters.get("skills"):
        skill_params = {f"skill_{i}": v for i, v in enumerate(filters["skills"])}
        placeholders = ",".join(f":skill_{i}" for i in range(len(filters["skills"])))
        conditions.append(f"r.skills && ARRAY[{placeholders}]::varchar[]")
        params.update(skill_params)

    if filters.get("cities"):
        city_params  = {f"city_{i}": v for i, v in enumerate(filters["cities"])}
        placeholders = ",".join(f":city_{i}" for i in range(len(filters["cities"])))
        conditions.append(f"r.city IN ({placeholders})")
        params.update(city_params)

    if filters.get("states"):
        state_params = {f"state_{i}": v for i, v in enumerate(filters["states"])}
        placeholders = ",".join(f":state_{i}" for i in range(len(filters["states"])))
        conditions.append(f"r.state IN ({placeholders})")
        params.update(state_params)

    if filters.get("experience_min") is not None:
        conditions.append("r.experience_years >= :exp_min")
        params["exp_min"] = filters["experience_min"]

    if filters.get("experience_max") is not None:
        conditions.append("r.experience_years <= :exp_max")
        params["exp_max"] = filters["experience_max"]

    where = "WHERE " + " AND ".join(conditions)
    sql   = text(f"""
        SELECT 
            r.*
        FROM resumes r
        INNER JOIN user_resumes ur ON r.id = ur.resume_id
        {where}
    """)

    return sql, params


# ── Main retrieval function ──────────────────────────────────────────────────

def retrieve_candidates(query: str, db, user_id: str) -> list:

    # 1. Fetch valid values fresh from DB
    valid = get_valid_filter_values(db, user_id)

    # 2. Early return if user has no resumes yet
    if not any([valid["domains"], valid["skills"], valid["cities"], valid["states"]]):
        return []

    # 3. Bind the dynamic schema as structured output

    from app.clients import get_llm
    llm = get_llm()
    CandidateFilter = make_filter_tool(valid)
    structured_llm  = llm.with_structured_output(CandidateFilter)

    # 4. Run
    raw = structured_llm.invoke([
        HumanMessage(content=f"""
Extract recruitment filters from this query.
Only use values explicitly listed in each field's description.
If no match exists, leave the field as an empty list.

Query: {query}
        """)
    ])

    # 5. Validate
    filters = validate_filters(raw.model_dump(), valid)

    # 6. Build and run SQL
    sql, params = build_sql(filters, user_id)
    logger.info(f"Constructed SQL: {sql}")
    logger.info(f"SQL Parameters: {params}")
    try:
        results = db.execute(sql, params).fetchall()
        return [dict(r._mapping) for r in results]
    except Exception as e:
        # Log the exact SQL for debugging
        logger.error(f"SQL error: {e}")
        logger.info(f"Filters applied: {filters}")
        raise
