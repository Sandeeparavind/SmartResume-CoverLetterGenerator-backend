from pydantic import BaseModel, Field
from typing import List, Optional
from typing import List

class CoverLetterRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    candidate_summary: str  # your background / highlights
    tone: str = "professional"  # e.g., professional, friendly, confident

class CoverLetterResponse(BaseModel):
    cover_letter: str

class SmartResumeRequest(BaseModel):
    resume_text: str          # full resume or key sections
    job_description: str      # JD or key requirements

class SmartResumeResponse(BaseModel):
    improved_resume: str      # rewritten / tailored version
    suggestions: List[str]    # bullet suggestions for improvement
