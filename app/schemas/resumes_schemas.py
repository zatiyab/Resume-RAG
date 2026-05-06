from pydantic import BaseModel,Field

class MetadataResponse(BaseModel):
    name: str = Field(description="Candidate's full name")
    location: str = Field(description="City name only, Title Case (e.g. 'Delhi', 'Noida', 'Bangalore')")
    skills: list[str] = Field(description="List of canonical skill names (e.g. JavaScript, Python, React)")
    experience_years: int = Field(description="Total years of experience, rounded down to nearest whole number")
    domain: list[str] = Field(description="Primary domain or role (e.g. 'Data Science', 'Frontend Development', 'Project Management')")
