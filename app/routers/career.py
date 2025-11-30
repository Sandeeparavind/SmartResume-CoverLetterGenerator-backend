from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..schemas import (
    CoverLetterRequest,
    CoverLetterResponse,
    SmartResumeRequest,
    SmartResumeResponse,
)
from ..services import career_service


router = APIRouter(prefix="/api/career", tags=["career"])


@router.post("/cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(
    resume: UploadFile = File(...),
    job_title: str = Form(...),
    company_name: str = Form(...),
    job_description: str = Form(...),
    tone: str = Form("professional"),
):
    allowed_types = ("application/pdf", "text/plain")

    if resume.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported resume file type. Please upload a PDF or plain text resume.",
        )

    resume_bytes = await resume.read()

    letter = career_service.generate_cover_letter_from_file(
        job_title=job_title,
        company_name=company_name,
        job_description=job_description,
        tone=tone,
        resume_bytes=resume_bytes,
        resume_content_type=resume.content_type,
    )

    return CoverLetterResponse(cover_letter=letter)

@router.post("/rewrite-summary-upload")
async def rewrite_summary_upload(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or plain text resume.",
        )

    file_bytes = await file.read()

    rewritten_summary = career_service.rewrite_summary_from_file(
        file_bytes=file_bytes,
        content_type=file.content_type,
        job_description=job_description,
    )

    return {"rewritten_summary": rewritten_summary}


@router.post("/smart-resume-upload")
async def generate_smart_resume_upload(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or plain text resume.",
        )

    file_bytes = await file.read()

    suggestions = career_service.improve_resume_from_file(
        file_bytes=file_bytes,
        content_type=file.content_type,
        job_description=job_description,
    )

    return {"suggestions": suggestions}
