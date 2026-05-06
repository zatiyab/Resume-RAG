from app.core.config import llm

def create_filter(user_query):

    PROMPT = """You are an expert query understanding system for a Resume RAG platform.

Your task is to analyze a recruiter query and generate structured SQL filter conditions for candidate metadata retrieval.

The candidate metadata table contains these columns:

- skills (varchar[])
- experience_years (integer)
- domain (varchar[])
- name (varchar)
- city (varchar)
- state (varchar)

Your job:
1. Extract filtering constraints from the recruiter query
2. Convert them into structured SQL-compatible filters
3. Do NOT generate full SQL queries
4. Only return valid JSON
5. Do NOT hallucinate fields not present in schema
6. Infer recruiter intent carefully
7. Handle partial/implicit experience requirements
8. Use ONLY canonical skill names
9. If a filter is not mentioned, omit it
10. Support fuzzy recruiter language

CANONICAL SKILL NAMES (STRICT):
Use ONLY these exact forms:

- JavaScript
- Python
- TypeScript
- React
- Node.js
- PHP
- Java
- C++

Never output aliases or variations such as:
- JS
- js
- NodeJS
- node
- Py
- Javascript

Normalize recruiter input into the canonical forms above.

IMPORTANT RULES:

- "python developer" → skills includes "Python"
- "react js developer" → skills includes "React"
- "node developer" → skills includes "Node.js"
- "js developer" → skills includes "JavaScript"
- "backend engineer" may map to domain includes "backend"
- "AI engineer" may map to domain includes "ai"
- "3+ years" → experience_years_gte = 3
- "less than 5 years" → experience_years_lt = 5
- "senior" usually means experience_years_gte = 5
- "junior" usually means experience_years_lt = 3
- "mid-level" usually means experience_years_between = [3,5]
- If recruiter mentions city/state, extract them separately
- If recruiter asks for a specific candidate name, use name
- Multiple skills should be treated as AND unless explicitly stated otherwise
- Return clean structured JSON only
- Never explain reasoning
- Never output non-canonical skill names

OUTPUT FORMAT:

{
  "skills_all": [],
  "skills_any": [],
  "domains": [],
  "experience_years_gte": null,
  "experience_years_lte": null,
  "experience_years_lt": null,
  "experience_years_gt": null,
  "experience_years_between": [],
  "city": null,
  "state": null,
  "name": null
}

EXAMPLES:

Recruiter Query:
"Need python developers with react js and 3+ years experience in Bangalore"

Output:
{
  "skills_all": ["Python", "React"],
  "skills_any": [],
  "domains": [],
  "experience_years_gte": 3,
  "city": "bangalore",
  "state": null,
  "name": null
}

Recruiter Query:
"Looking for frontend or node developers in Delhi"

Output:
{
  "skills_all": [],
  "skills_any": ["Node.js"],
  "domains": ["frontend"],
  "city": "delhi",
  "state": null,
  "name": null
}

Recruiter Query:
"Junior java developers from Maharashtra"

Output:
{
  "skills_all": ["Java"],
  "skills_any": [],
  "domains": [],
  "experience_years_lt": 3,
  "state": "maharashtra"
}

Recruiter Query:
"Need js and typescript engineers"

Output:
{
  "skills_all": ["JavaScript", "TypeScript"],
  "skills_any": [],
  "domains": [],
  "city": null,
  "state": null,
  "name": null
}

Now analyze the recruiter query and generate the JSON filters.

Recruiter Query:
{user_query}
"""
    prompt = PROMPT.replace("{user_query}", user_query)
    response = llm.invoke(prompt)
    response_content = response.content.strip()
    try:
        import json
        filters = json.loads(response_content)
        return filters
    except json.JSONDecodeError:
        print("Failed to parse JSON response:")
        print(response_content)
        return None
    





from sqlalchemy import  and_, func


from app.models.resumes import ResumesMetadata



def apply_resume_filters(query, filters: dict):
    conditions = []

    def _normalize_scalar_filter(value):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    return item.strip()
            return None

        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None

        return value

    # -------------------------
    # Skills (ALL)
    # PostgreSQL array contains
    # -------------------------
    skills_all = filters.get("skills_all")
    if skills_all:
        conditions.append(
            ResumesMetadata.skills.contains(skills_all)
        )

    # -------------------------
    # Skills (ANY)
    # PostgreSQL overlap operator
    # -------------------------
    skills_any = filters.get("skills_any")
    if skills_any:
        conditions.append(
            ResumesMetadata.skills.overlap(skills_any)
        )

    # -------------------------
    # Domains
    # -------------------------
    domains = filters.get("domains")
    if domains:
        conditions.append(
            ResumesMetadata.domain.overlap(domains)
        )

    # -------------------------
    # Experience filters
    # -------------------------
    if filters.get("experience_years_gte") is not None:
        conditions.append(
            ResumesMetadata.experience_years >= filters["experience_years_gte"]
        )

    if filters.get("experience_years_lte") is not None:
        conditions.append(
            ResumesMetadata.experience_years <= filters["experience_years_lte"]
        )

    if filters.get("experience_years_gt") is not None:
        conditions.append(
            ResumesMetadata.experience_years > filters["experience_years_gt"]
        )

    if filters.get("experience_years_lt") is not None:
        conditions.append(
            ResumesMetadata.experience_years < filters["experience_years_lt"]
        )

    experience_between = filters.get("experience_years_between")
    if experience_between and len(experience_between) == 2:
        conditions.append(
            ResumesMetadata.experience_years.between(
                experience_between[0],
                experience_between[1]
            )
        )

    # -------------------------
    # City
    # -------------------------
    city = _normalize_scalar_filter(filters.get("city"))
    if city:
        conditions.append(
            func.lower(ResumesMetadata.city) == city.lower()
        )

    # -------------------------
    # State
    # -------------------------
    state = _normalize_scalar_filter(filters.get("state"))
    if state:
        conditions.append(
            func.lower(ResumesMetadata.state) == state.lower()
        )

    # -------------------------
    # Name
    # -------------------------
    name = _normalize_scalar_filter(filters.get("name"))
    if name:
        conditions.append(
            ResumesMetadata.name.ilike(f"%{name}%")
        )

    # -------------------------
    # Apply conditions
    # -------------------------
    if conditions:
        query = query.where(and_(*conditions))

    return query

